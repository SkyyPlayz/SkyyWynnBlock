#!/usr/bin/env python3
"""make_icons.py - SkyWynn icon drafts 2026-10-13 (cloud): Rarity Sigils, Hub Shard + 6 Shard Portals, Nexus of the Void.

Deterministic (Pillow only, no randomness, no timestamps): two runs give the same bytes.
Style = the approved menu icons (art/menu-icons/): hard alpha, 1 px violet-black outline tinted toward the part it touches,
light from the top left (lit bevel top / left, dark bevel bottom / right), contact shadows, every pixel from a 7-step ramp
(shadows lean violet, lights lean warm), no #000000 / #ffffff. All geometry and pixels are original.

Run:  python3 research/cloud/icons-1013/make_icons.py
Out (next to this script): icons/<id>.png (64 x 64; the Nexus also 128 x 128), sheet-sigils.png, sheet-shards.png,
sheet-nexus.png, manifest.json
"""
import hashlib
import json
import math
import os
from collections import deque

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ICONS = os.path.join(HERE, "icons")


# ------------------------------------------------------------------ colour
def hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


SHADOW = hx("#1c1434")      # shadows lean violet / blue
LIGHT = hx("#fff2d0")       # lights lean warm
OUTLINE = hx("#120e1c")     # the family outline


def ramp(base, dt=(0.80, 0.56, 0.30), lt=(0.26, 0.50, 0.74), dark=SHADOW, light=LIGHT):
    """7 steps, index 3 = base. Never pure black / white."""
    b = hx(base) if isinstance(base, str) else base
    r = [mix(b, dark, t) for t in dt] + [b] + [mix(b, light, t) for t in lt]
    out = []
    for c in r:
        if c == (0, 0, 0):
            c = (10, 8, 16)
        if c == (255, 255, 255):
            c = (252, 250, 242)
        out.append(c)
    return tuple(out)


def ramp_hex(*hs):
    assert len(hs) == 7
    return tuple(hx(h) for h in hs)


# ------------------------------------------------------------------ shapes (predicates on pixel centres)
def poly(pts):
    pts = list(pts)

    def f(x, y):
        inside = False
        j = len(pts) - 1
        for i in range(len(pts)):
            xi, yi = pts[i]
            xj, yj = pts[j]
            if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
                inside = not inside
            j = i
        return inside
    return f


def circ(cx, cy, r):
    return lambda x, y: (x - cx) ** 2 + (y - cy) ** 2 <= r * r


def ell(cx, cy, rx, ry):
    return lambda x, y: ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0


def rell(cx, cy, rx, ry, deg):
    ca, sa = math.cos(math.radians(deg)), math.sin(math.radians(deg))

    def f(x, y):
        dx, dy = x - cx, y - cy
        u, v = dx * ca + dy * sa, -dx * sa + dy * ca
        return (u / rx) ** 2 + (v / ry) ** 2 <= 1.0
    return f


def rect(x0, y0, x1, y1):
    return lambda x, y: x0 <= x < x1 and y0 <= y < y1


def U(*fs):
    return lambda x, y: any(f(x, y) for f in fs)


def D(a, *bs):
    return lambda x, y: a(x, y) and not any(b(x, y) for b in bs)


def I(a, b):
    return lambda x, y: a(x, y) and b(x, y)


def seg(x0, y0, x1, y1, w):
    """a thick line segment (capsule) of width w"""
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy

    def f(x, y):
        t = max(0.0, min(1.0, ((x - x0) * dx + (y - y0) * dy) / L2))
        px, py = x0 + t * dx, y0 + t * dy
        return (x - px) ** 2 + (y - py) ** 2 <= (w / 2.0) ** 2
    return f


def mirror(pts, cx=32):
    return [(2 * cx - x, y) for x, y in pts]


def hexagon(cx, cy, r):
    return [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in (-90, -30, 30, 90, 150, 210)]


N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


# ------------------------------------------------------------------ canvas
class Icon:
    def __init__(self, w=64, h=64):
        self.w, self.h = w, h
        self.p = {}          # (x, y) -> (ramp, idx)
        self.top = {}        # sparkles etc. drawn after the outline: (x, y) -> rgb

    def mask(self, f):
        return {(x, y) for y in range(self.h) for x in range(self.w) if f(x + 0.5, y + 0.5)}

    @staticmethod
    def dist(m):
        d, q = {}, deque()
        for p in m:
            for dx, dy in N4:
                if (p[0] + dx, p[1] + dy) not in m:
                    d[p] = 1
                    q.append(p)
                    break
        while q:
            p = q.popleft()
            for dx, dy in N4:
                n = (p[0] + dx, p[1] + dy)
                if n in m and n not in d:
                    d[n] = d[p] + 1
                    q.append(n)
        return d

    def add(self, f, rp, base=3, bevel=True, inset=False, grad=0.0, line=False, shadow=False, glow=False,
            fn=None, m=None):
        """Paint a shape. bevel = lit top-left rim, dark bottom-right rim; inset flips it (a recessed field);
        grad = a soft top-left -> bottom-right gradient (steps); glow = brighter toward the middle;
        line = 1 px darkest inner line where the shape sits over something; shadow = contact shadow on what is behind;
        fn(x, y, idx) -> idx lets a caller pattern the fill."""
        m = self.mask(f) if m is None else m
        if not m:
            return m
        if shadow:
            sh = set()
            for (x, y) in m:
                for o in ((1, 1), (1, 2), (0, 1)):
                    q = (x + o[0], y + o[1])
                    if q not in m and q in self.p:
                        sh.add(q)
            for q in sh:
                r, i = self.p[q]
                self.p[q] = (r, max(0, i - 2))
        d = self.dist(m)
        xs = [p[0] for p in m]
        ys = [p[1] for p in m]
        cx, cy = (min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0
        span = max(1.0, (max(xs) - min(xs)) + (max(ys) - min(ys))) / 2.0
        old = dict(self.p)
        for p in m:
            x, y = p
            k = d[p]
            idx = float(base)
            if glow:
                idx += min(k - 1, 3)
            elif bevel and k <= 2:
                nx = ny = 0.0
                for oy in range(-2, 3):
                    for ox in range(-2, 3):
                        if (x + ox, y + oy) not in m:
                            nx += ox
                            ny += oy
                L = math.hypot(nx, ny)
                if L > 0:
                    s = (-nx - ny) / (L * math.sqrt(2.0))   # +1 = faces the top-left light
                    if inset:
                        s = -s
                    idx += (2.0 if k == 1 else 1.0) * s
            if grad:
                idx -= grad * ((x - cx) + (y - cy)) / span
            idx = int(round(idx))
            if fn is not None:
                idx = fn(x, y, idx)
            idx = max(0, min(len(rp) - 1, idx))
            if line and k == 1:
                for dx, dy in N4:
                    n = (x + dx, y + dy)
                    if n not in m and n in old:
                        idx = 0
                        break
            self.p[p] = (rp, idx)
        return m

    def ring_around(self, m, rp, idx=0, width=1):
        """paint a halo / line of `width` px around mask m (over whatever is there, and onto empty pixels)."""
        cur = set(m)
        for _ in range(width):
            nxt = set()
            for (x, y) in cur:
                for dx, dy in N4:
                    n = (x + dx, y + dy)
                    if n not in m and 0 <= n[0] < self.w and 0 <= n[1] < self.h:
                        nxt.add(n)
            for n in nxt:
                self.p[n] = (rp, idx)
            m = m | nxt
            cur = nxt

    def tint_existing(self, m, delta):
        for q in m:
            if q in self.p:
                r, i = self.p[q]
                self.p[q] = (r, max(0, min(len(r) - 1, i + delta)))

    def sparkle(self, x, y, rp, big=False):
        self.top[(x, y)] = rp[6]
        for dx, dy in N4:
            self.top[(x + dx, y + dy)] = rp[5]
        if big:
            for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
                self.top[(x + dx, y + dy)] = rp[4]

    def image(self):
        im = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        px = im.load()
        for (x, y), (r, i) in self.p.items():
            if 0 <= x < self.w and 0 <= y < self.h:
                px[x, y] = r[i] + (255,)
        for y in range(self.h):
            for x in range(self.w):
                if (x, y) in self.p:
                    continue
                for dx, dy in N4:
                    n = (x + dx, y + dy)
                    if n in self.p:
                        r, _ = self.p[n]
                        px[x, y] = mix(OUTLINE, r[0], 0.22) + (255,)
                        break
        for (x, y), c in self.top.items():
            if 0 <= x < self.w and 0 <= y < self.h and (x, y) not in self.p:
                px[x, y] = c + (255,)
        return im


# ------------------------------------------------------------------ materials
IRON = ramp_hex("#24222e", "#3e3f4c", "#5a5e6c", "#7c818e", "#a0a5b0", "#c2c6cc", "#dcdcd8")
GOLD = ramp_hex("#3a2210", "#6e4212", "#a8691c", "#d4982e", "#eebd4c", "#f8da80", "#fcefb8")
ROSE = ramp_hex("#3a1a26", "#6e3438", "#a05650", "#c87c6e", "#e2a08c", "#f2c4ae", "#fbe2d2")
PLAT = ramp_hex("#262c3c", "#48546a", "#6e7e94", "#98a8bc", "#bccada", "#dae4ec", "#eef2f2")
BLKSTEEL = ramp_hex("#18121e", "#2a2230", "#3e3446", "#564a5c", "#726474", "#948290", "#b8a6ae")
OBSID = ramp_hex("#140c22", "#22163a", "#342254", "#4a3270", "#66478e", "#8a68ae", "#b496cc")
STONE = ramp_hex("#1e1a28", "#36323e", "#4e4a54", "#68646a", "#848078", "#a29c90", "#c2baa8")
SOIL = ramp_hex("#22141c", "#3c2420", "#5a3626", "#7a4c30", "#9a6640", "#b8845a", "#d4a87c")
GRASS = ramp_hex("#14261e", "#1e4228", "#2c6230", "#3e8434", "#62a640", "#8ec45a", "#bcdc84")
CREAM = ramp_hex("#3a2c34", "#7a6458", "#b09a80", "#dccaa4", "#f2e6c4", "#fbf3dc", "#fdf9ec")
SKYGEM = ramp("#58b8ec")

RAR = [  # name, Skyy-locked rarity colour (tools/skyyui.py RARITY), frame metal, ornaments
    ("Normal", "#FFFFFF", IRON, 0),
    ("Unique", "#FFFF55", GOLD, 1),
    ("Rare", "#FF55FF", ROSE, 2),
    ("Legendary", "#55FFFF", PLAT, 3),
    ("Fabled", "#FF5555", BLKSTEEL, 4),
    ("Mythic", "#CC66CC", OBSID, 5),
]


def glow_ramp(c):
    """rarity glyph ramp: the rarity colour at idx 4, deep shades below, a warm-white core above."""
    b = hx(c)
    if b == (255, 255, 255):
        b = (226, 228, 236)          # Normal = white -> a pale silver glow (no pure white)
    r = [mix(b, SHADOW, 0.78), mix(b, SHADOW, 0.58), mix(b, SHADOW, 0.36), mix(b, SHADOW, 0.16), b,
         mix(b, (255, 250, 236), 0.45), mix(b, (255, 250, 236), 0.78)]
    return tuple(x if x != (255, 255, 255) else (252, 250, 242) for x in r)


def field_ramp(c):
    b = hx(c)
    if b == (255, 255, 255):
        b = (150, 156, 176)
    base = mix(b, (18, 12, 32), 0.80)
    return ramp(base, dt=(0.70, 0.45, 0.22), lt=(0.10, 0.22, 0.38), light=b)


# ------------------------------------------------------------------ 1. SIGILS
def sigil(rank):
    name, col, metal, orn = RAR[rank]
    G = glow_ramp(col)
    F = field_ramp(col)
    ic = Icon()
    cx, cy = 32, 33
    # side blades (Fabled, Mythic) - gold, behind the plate
    if orn >= 4:
        blade = [(13, 24), (3.5, 19), (7.5, 30), (2.5, 33.5), (7.5, 37), (3.5, 47), (13, 42)]
        ic.add(poly(blade), GOLD, base=3, grad=0.8)
        ic.add(poly(mirror(blade)), GOLD, base=3, grad=0.8)
        # a red / violet inlay line in each blade
        ic.add(poly([(11, 27), (7, 25.5), (9, 32), (11, 31)]), G, base=3, bevel=False)
        ic.add(poly(mirror([(11, 27), (7, 25.5), (9, 32), (11, 31)])), G, base=3, bevel=False)
    # crown (Mythic) - gold, behind the plate
    if orn >= 5:
        crown = [(21, 15), (20.5, 6), (25.5, 9.5), (32, 1.5), (38.5, 9.5), (43.5, 6), (43, 15)]
        ic.add(poly(crown), GOLD, base=3, grad=0.6)
    # the plate (outer hex) + its recessed field (inner hex)
    outer = poly(hexagon(cx, cy, 23.5))
    ic.add(outer, metal, base=3, grad=0.9, shadow=orn >= 4)
    if orn >= 2:       # a second trim line on the frame (Rare+)
        trim = D(poly(hexagon(cx, cy, 20.5)), poly(hexagon(cx, cy, 19.5)))
        ic.add(trim, metal, base=2, bevel=False)
    inner = poly(hexagon(cx, cy, 18.5))
    fm = ic.add(inner, F, base=2, inset=True, grad=0.6)
    # the glyph: an upward arrow (= upgrade), a bar under it from Rare up
    head = poly([(32, 14.5), (42.5, 26), (36.5, 26), (36.5, 38.5), (27.5, 38.5), (27.5, 26), (21.5, 26)])
    glyph = head
    if orn >= 2:
        glyph = U(head, rect(23, 41, 41, 44))
    gm = ic.mask(glyph)
    # soft rarity-tinted glow in the field round the glyph
    halo = set()
    for (x, y) in gm:
        for oy in range(-2, 3):
            for ox in range(-2, 3):
                q = (x + ox, y + oy)
                if q in fm and q not in gm and abs(ox) + abs(oy) <= 3:
                    halo.add(q)
    for q in halo:
        r, i = ic.p[q]
        ic.p[q] = (r, min(6, i + 2))
    ic.add(None, G, base=3, glow=True, m=gm)
    # rivets on the frame (Rare+): at the 6 corners, just inside
    if orn >= 2:
        for (x, y) in hexagon(cx, cy, 21.2):
            rm = ic.add(circ(x, y, 1.6), metal, base=5, bevel=False)
            for q in rm:                       # a dark lower-right half: the rivet reads round
                if q[0] + q[1] > x + y - 0.5:
                    ic.p[q] = (metal, 2)
    # gem at the top corner (Legendary+), in the rarity colour
    if orn >= 3:
        ic.add(circ(32, 12.2, 3.1), G, base=3, line=True, shadow=True,
               fn=lambda x, y, i: i + (2 if (x <= 31 and y <= 11) else 0))
    # bottom gem (Mythic)
    if orn >= 5:
        ic.add(circ(32, 53.6, 2.6), G, base=3, line=True,
               fn=lambda x, y, i: i + (2 if (x <= 31 and y <= 53) else 0))
    # sparkles
    if orn >= 3:
        ic.sparkle(55, 9, G, big=orn >= 4)
    if orn >= 5:
        ic.sparkle(8, 55, G)
        ic.sparkle(58, 56, G)
    return ic


# ------------------------------------------------------------------ 2. HUB SHARD + SHARD PORTALS
SHARDS = [  # id suffix, label, crystal colour, symbol fn name, worker (docs/answered/skills.md 2026-10-11 SHARDS 3)
    ("Mining", "Mining", "#4aa6e8", "pickaxe"),
    ("Foraging", "Foraging", "#46b856", "pine"),
    ("Farming", "Farming", "#e2b532", "wheat"),
    ("Ranching", "Ranching", "#e0864a", "cow"),
    ("Orchard", "Orchard", "#ec6aa6", "apple"),
    ("Combat", "Combat", "#d83c48", "swords"),
]
VOID = "#9466ee"


def crystal_ramp(c):
    return ramp(c, dt=(0.82, 0.60, 0.32), lt=(0.28, 0.52, 0.76))


def symbol(kind, ox=0, oy=0):
    """a 16 x 16-ish symbol centred near (32, 27) + offset. Returns a predicate."""
    def T(pts):
        return [(x + ox, y + oy) for x, y in pts]
    if kind == "pickaxe":
        # diagonal pickaxe: handle bottom-left -> top-right, a curved head across its top end
        hx0, hy0, hx1, hy1 = 24.5 + ox, 38 + oy, 37.5 + ox, 21 + oy
        L = math.hypot(hx1 - hx0, hy1 - hy0)
        dx, dy = (hx1 - hx0) / L, (hy1 - hy0) / L
        px_, py_ = -dy, dx
        Hx, Hy = hx1 + 0.6 * dx, hy1 + 0.6 * dy
        outer, inner = [], []
        for j in range(13):
            t = -1 + j / 6.0
            cxp = Hx + 10.0 * t * px_ - 3.6 * t * t * dx
            cyp = Hy + 10.0 * t * py_ - 3.6 * t * t * dy
            w = 2.3 * (1 - 0.72 * abs(t))
            outer.append((cxp + w * dx, cyp + w * dy))
            inner.append((cxp - w * dx, cyp - w * dy))
        return U(poly(outer + inner[::-1]), seg(hx0, hy0, hx1, hy1, 3.2))
    if kind == "pine":
        return U(poly(T([(32, 15.5), (38.5, 23), (25.5, 23)])), poly(T([(32, 19.5), (40.5, 29.5), (23.5, 29.5)])),
                 poly(T([(32, 24), (42, 35), (22, 35)])), rect(30 + ox, 34 + oy, 34 + ox, 38.5 + oy))
    if kind == "wheat":       # separate parts: every grain gets its own dark line, so the ear reads as grains
        parts = [rect(31 + ox, 24 + oy, 33 + ox, 39.5 + oy), rell(32 + ox, 18.6 + oy, 2.0, 3.2, 0)]
        for gy in (23.4, 28.6, 33.8):
            parts.append(rell(28.4 + ox, gy + oy, 3.6, 2.0, -42))
            parts.append(rell(35.6 + ox, gy + oy, 3.6, 2.0, 42))
        return parts
    if kind == "cow":
        head = ell(32 + ox, 27.5 + oy, 6.2, 7.6)
        hornL = poly(T([(27, 22), (23, 21), (21, 17), (23.4, 17.6), (25.4, 19.4), (28.6, 20)]))
        hornR = poly(T(mirror([(27, 22), (23, 21), (21, 17), (23.4, 17.6), (25.4, 19.4), (28.6, 20)])))
        earL = ell(23.6 + ox, 25 + oy, 3.4, 1.9)
        earR = ell(40.4 + ox, 25 + oy, 3.4, 1.9)
        muzzle = ell(32 + ox, 34 + oy, 6.6, 4.0)
        return U(head, hornL, hornR, earL, earR, muzzle)
    if kind == "apple":
        body = U(circ(28.4 + ox, 30.5 + oy, 6.4), circ(35.6 + ox, 30.5 + oy, 6.4), ell(32 + ox, 34 + oy, 7.0, 5.2))
        body = D(body, ell(32 + ox, 24.0 + oy, 2.2, 2.2), ell(32 + ox, 40.2 + oy, 1.6, 1.0))
        stem = seg(31.8 + ox, 26.5 + oy, 33.2 + ox, 19.5 + oy, 1.8)
        leaf = poly(T([(34.6, 22.2), (36.6, 18.4), (41.5, 17.0), (40.4, 20.4), (36.8, 22.6)]))
        return U(body, stem, leaf)
    if kind == "swords":      # two swords painted one over the other, gold guards
        parts = []
        for sgn in (1, -1):
            def P(x, y):
                return (32 + sgn * (x - 32) + ox, y + oy)
            blade = [P(25.4, 32.2), P(38.0, 18.6), P(41.2, 16.4), P(39.4, 20.0), P(27.8, 34.6)]
            h0, h1 = P(26.0, 35.6), P(22.8, 38.8)
            pm = P(22.0, 39.6)
            g0, g1 = P(23.2, 30.2), P(30.0, 37.0)
            parts.append(U(poly(blade), seg(h0[0], h0[1], h1[0], h1[1], 2.4), circ(pm[0], pm[1], 1.9)))
            parts.append((seg(g0[0], g0[1], g1[0], g1[1], 2.6), "gold"))
        return parts
    raise ValueError(kind)


def symbol_details(ic, kind, C, ox=0, oy=0):
    """dark marks drawn ON the cream symbol (eyes, nostrils ...), crystal ramp idx 0."""
    if kind == "cow":
        for p in ((29 + ox, 27 + oy), (34 + ox, 27 + oy), (29 + ox, 34 + oy), (34 + ox, 34 + oy)):
            ic.p[p] = (C, 0)
        for x in range(27 + ox, 37 + ox):                 # the muzzle line
            if (x, 31 + oy) in ic.p and ic.p[(x, 31 + oy)][0] is CREAM:
                ic.p[(x, 31 + oy)] = (CREAM, 2)
    if kind == "wheat":
        pass


def swirl_fn(cx, cy):
    def fn(x, y, i):
        dx, dy = x + 0.5 - cx, y + 0.5 - cy
        r = math.hypot(dx, dy)
        a = math.atan2(dy, dx)
        v = math.sin(2 * a + r * 0.55)
        i = i + (2 if v > 0.45 else (1 if v > -0.1 else 0))
        return i - (1 if r < 4.5 else 0)
    return fn


CRYSTAL_MAIN = [(32, 3), (45.5, 13), (45.5, 41), (32, 50), (18.5, 41), (18.5, 13)]


def crystal(ic, C, symkind=None, star=False, oy=0):
    """the shared family crystal: a hex prism shard, faceted rim, a portal swirl window, a cream symbol inside."""
    pts = [(x, y + oy) for x, y in CRYSTAL_MAIN]
    main = poly(pts)
    m = ic.add(main, C, base=4, grad=1.2, shadow=True)
    # facets: left face lighter, right face darker, top facets
    left = I(main, lambda x, y: x < 24)
    right = I(main, lambda x, y: x > 40)
    ic.tint_existing(ic.mask(left), +1)
    ic.tint_existing(ic.mask(right), -1)
    topL = I(main, poly([(32, 3 + oy), (18, 13 + oy), (24, 15 + oy), (32, 9 + oy)]))
    topR = I(main, poly([(32, 3 + oy), (46, 13 + oy), (40, 15 + oy), (32, 9 + oy)]))
    ic.tint_existing(ic.mask(topL), +1)
    ic.tint_existing(ic.mask(topR), 0)
    # facet edge lines (bright on the light side, dark on the other)
    for y in range(int(15 + oy), int(42 + oy)):
        if (23, y) in m:
            ic.p[(23, y)] = (C, 6)
        if (40, y) in m:
            ic.p[(40, y)] = (C, 1)
    # the window: a recessed portal swirl
    win = poly([(32, 11 + oy), (39.5, 17 + oy), (39.5, 39 + oy), (32, 44.5 + oy), (24.5, 39 + oy), (24.5, 17 + oy)])
    ic.add(win, C, base=1, inset=True, fn=swirl_fn(32, 27.5 + oy))
    if symkind:
        parts = symbol(symkind, 0, oy)
        if not isinstance(parts, list):
            parts = [parts]
        for part in parts:
            pr, rp = (part[0], GOLD) if isinstance(part, tuple) else (part, CREAM)
            sm = ic.mask(pr)
            ic.ring_around(sm, C, idx=0)
            ic.add(None, rp, base=4, m=sm, grad=0.6)
        symbol_details(ic, symkind, C, 0, oy)
    if star:
        s = []
        for k in range(16):
            a = math.radians(-90 + k * 22.5)
            rr = (11.0 if k % 4 == 0 else (6.4 if k % 2 == 0 else 3.6))
            s.append((32 + rr * math.cos(a), 27.5 + oy + rr * math.sin(a)))
        sm = ic.mask(poly(s))
        ic.ring_around(sm, C, idx=0)
        # pinwheel bevel like the menu emblem's compass star
        def pin(x, y, i):
            dx, dy = x + 0.5 - 32, y + 0.5 - (27.5 + oy)
            a = math.atan2(dy, dx) % (math.pi / 2)
            return i + (1 if a < math.pi / 4 else -1)
        ic.add(None, GOLD, base=4, bevel=False, m=sm, fn=pin)
        ic.add(circ(32, 27.5 + oy, 2.2), SKYGEM, base=4, fn=lambda x, y, i: i + (1 if x <= 31 and y <= 27 + oy else 0))
    return m


def side_shards(ic, C):
    L = [(19.5, 46), (11.5, 40), (10, 29.5), (14, 24), (20, 33)]
    ic.add(poly(L), C, base=3, grad=1.0)
    ic.tint_existing(ic.mask(poly([(14, 24), (10, 29.5), (11.5, 40), (14.5, 41.5), (15, 28)])), +1)
    R = mirror([(19.5, 46), (12, 41), (11, 33), (14.5, 28.5), (20, 36)])
    ic.add(poly(R), C, base=2, grad=1.0)


def island_base(ic):
    """the shared floating rock (a shard IS a mini island): grass top, soil band, stepped rock underside."""
    rock = poly([(9, 49), (55, 49), (52, 54), (45, 57.5), (38, 59), (34, 62), (29, 61.5), (25, 58.5), (17, 56.5), (11, 53)])
    ic.add(rock, STONE, base=3, grad=1.0)
    ic.tint_existing(ic.mask(I(rock, lambda x, y: y > 56)), -1)
    ic.add(poly([(28, 58), (33, 58), (32, 61.5), (30, 61)]), STONE, base=2, bevel=False)
    soil = ell(32, 48.4, 23.5, 4.2)
    ic.add(soil, SOIL, base=3, grad=0.8)
    top = ell(32, 46.6, 23, 3.6)
    ic.add(top, GRASS, base=4, grad=0.9)
    for x in (13, 19, 27, 38, 47, 51):     # grass hanging over the soil edge
        ic.p[(x, 50)] = (GRASS, 3)
        ic.p[(x, 51)] = (GRASS, 2)


def shard_portal(i):
    _, _, col, kind = SHARDS[i]
    C = crystal_ramp(col)
    ic = Icon()
    island_base(ic)
    side_shards(ic, C)
    crystal(ic, C, symkind=kind, oy=0)
    # the crystal sits IN the grass: re-grass the front lip over its foot
    lip = I(ell(32, 46.6, 23, 3.6), lambda x, y: y > 47.4)
    ic.add(lip, GRASS, base=3, bevel=False, line=True)
    ic.sparkle(54, 8, C)
    ic.sparkle(8, 14, C)
    return ic


def hub_shard():
    C = crystal_ramp(VOID)
    ic = Icon()
    # loose shard + a gold clasp with a ring (it is a carried key item, not a placed portal)
    loop = D(circ(32, 56.5, 4.6), circ(32, 56.5, 2.2))
    ic.add(loop, GOLD, base=3, grad=0.6)
    crystal(ic, C, star=True, oy=-1)
    clasp = poly([(21, 40), (25.5, 44.5), (32, 49), (38.5, 44.5), (43, 40), (43.5, 45), (36, 51.5), (32, 52.5), (28, 51.5),
                  (20.5, 45)])
    ic.add(clasp, GOLD, base=3, grad=0.8, line=True, shadow=True)
    for p in ((24, 45), (40, 45), (32, 50)):
        ic.p[p] = (GOLD, 6)
    # prongs up the sides
    ic.add(poly([(17.5, 30), (20.5, 29), (21.5, 41), (19, 42)]), GOLD, base=3, line=True)
    ic.add(poly(mirror([(17.5, 30), (20.5, 29), (21.5, 41), (19, 42)])), GOLD, base=2, line=True)
    ic.sparkle(54, 8, C, big=True)
    ic.sparkle(9, 50, C)
    return ic


# ------------------------------------------------------------------ 3. NEXUS OF THE VOID
VOIDR = ramp_hex("#0e0a1a", "#1a1230", "#2a1c4c", "#46307a", "#6c4cb0", "#a07ee0", "#d8c4f6")
EMBER = ramp_hex("#2a1028", "#5a1a46", "#94306a", "#d0507a", "#f08a74", "#fac088", "#fde6be")
SOUL = ramp_hex("#0c2a34", "#16505e", "#22808e", "#3cb4bc", "#6ee0dc", "#aef4ea", "#e2fcf4")
LINE = ramp_hex("#1a1230", "#2c1e50", "#43307a", "#6448a8", "#8c6cd4", "#b49aec", "#ddd0f8")


def nexus(S):
    """S = 128 (the /rebirth centre emblem) or 64 (item / button icon). One drawing, two detail levels."""
    k = S / 128.0
    c = S / 2.0
    ic = Icon(S, S)
    big = S >= 128
    # the radiating tree: 8 branches out of the hole; inner nodes lit (spent), outer ones dim (to come)
    nodes = []
    for b in range(8):
        a = math.radians(-90 + b * 45)
        r0, r1 = 33 * k, (52 if big else 56) * k
        x0, y0 = c + r0 * math.cos(a), c + r0 * math.sin(a)
        x1, y1 = c + r1 * math.cos(a), c + r1 * math.sin(a)
        ic.add(seg(x0, y0, x1, y1, max(2.0, 2.6 * k)), LINE, base=3, bevel=False)
        nodes.append((x1, y1, 4.6 * k if big else 3.4, b % 2 == 0))
        if big:
            for s in (-1, 1):
                a2 = a + s * math.radians(13)
                x2, y2 = c + 60 * math.cos(a2), c + 60 * math.sin(a2)
                ic.add(seg(x1, y1, x2, y2, 2.0), LINE, base=2, bevel=False)
                nodes.append((x2, y2, 3.0, False))
            xm, ym = c + 42 * math.cos(a), c + 42 * math.sin(a)
            nodes.append((xm, ym, 3.2, True))
    for (x, y, r, lit) in nodes:
        if lit:
            ic.add(circ(x, y, r), EMBER, base=4, line=True, fn=lambda xx, yy, i, x=x, y=y: i + (1 if xx + 0.5 < x and yy + 0.5 < y else 0))
        else:
            ic.add(circ(x, y, r), LINE, base=3, line=True)
    # the accretion swirl: a full disc of void with 4 bright spiral arms, hot (ember) near the hole, violet further out
    R = 31 * k
    R0 = 10 * k

    def arm(x, y):
        dx, dy = x - c, y - c
        r = math.hypot(dx, dy)
        a = math.atan2(dy, dx)
        return math.sin(4 * a - 7.5 * math.log(r / R0 + 0.35)), r

    def disk_in(x, y):
        v, r = arm(x, y)
        if r < R0 or r > R:
            return False
        edge = (r - R0) / (R - R0)
        return r <= 0.80 * R or v > -0.2 + 1.1 * (edge - 0.8) / 0.2

    dm = ic.mask(disk_in)

    def disk_fn(x, y, i):
        v, r = arm(x + 0.5, y + 0.5)
        t = (r - R0) / (R - R0)
        base = 2.2 - 1.6 * t                 # the dim disc, a little brighter inward
        if v > 0.2:
            base += 2.4 + 1.0 * (1 - t)       # the arms
        elif v > -0.35:
            base += 0.8
        return int(round(base))
    hot = {p for p in dm if math.hypot(p[0] + 0.5 - c, p[1] + 0.5 - c) < 17.5 * k}
    ic.add(None, VOIDR, bevel=False, m=dm - hot, fn=disk_fn)
    ic.add(None, EMBER, bevel=False, m=hot, fn=lambda x, y, i: disk_fn(x, y, i) + 1)
    # the soul being pulled in (the void imprints your soul): a cyan wisp, round head toward the hole, tail curling out
    hr = 3.6 * k if big else 2.4
    ang = math.radians(212)
    hcx, hcy = c + 21.5 * k * math.cos(ang), c + 21.5 * k * math.sin(ang)
    wm = ic.mask(circ(hcx, hcy, hr))
    for j in range(1, 9):
        t = j / 8.0
        aa = ang - 0.75 * t
        rr = (21.5 + 10.5 * t) * k
        w = hr * (1 - 0.8 * t)
        wm |= ic.mask(circ(c + rr * math.cos(aa), c + rr * math.sin(aa), max(0.7, w)))
    ic.ring_around(wm, VOIDR, idx=0)
    ic.add(None, SOUL, base=3, m=wm, grad=0.8)
    if big:   # two eye dots: it is a soul, not a comet
        for ex in (-1.2, 1.2):
            ex_, ey_ = hcx + ex * math.cos(ang + math.pi / 2), hcy + ex * math.sin(ang + math.pi / 2)
            ic.p[(int(ex_), int(ey_))] = (SOUL, 0)
    # photon ring + the hole (no pure black: the deepest void violet)
    ic.add(D(circ(c, c, 13.2 * k), circ(c, c, 10.2 * k)), VOIDR, base=6, glow=False, bevel=False,
           fn=lambda x, y, i: 6 if (x + y + 1 < 2 * c) else 5)
    hole = ic.add(circ(c, c, 10.2 * k), VOIDR, base=0, bevel=False)
    # a faint inner rim so the hole reads as a sphere, not a flat disc
    for p in hole:
        r = math.hypot(p[0] + 0.5 - c, p[1] + 0.5 - c)
        if r > 8.6 * k and (p[0] + p[1] + 1) > 2 * c:
            ic.p[p] = (VOIDR, 1)
    ic.sparkle(int(c + 40 * k), int(c - 44 * k), LINE, big=big)
    ic.sparkle(int(c - 46 * k), int(c + 38 * k), EMBER)
    return ic


# ------------------------------------------------------------------ sheets
NAVY = (11, 21, 36)
PAGE = (22, 24, 34)
LIGHTBG = (226, 228, 234)
TXT = (232, 226, 210)
DIM = (150, 156, 176)


def font(n):
    return ImageFont.load_default(size=n)


def checker(d, x, y, w, h, s=8):
    for yy in range(0, h, s):
        for xx in range(0, w, s):
            c = (52, 56, 74) if ((xx // s + yy // s) % 2 == 0) else (44, 48, 64)
            d.rectangle([x + xx, y + yy, x + min(xx + s, w) - 1, y + min(yy + s, h) - 1], fill=c)


def paste_scaled(sheet, im, x, y, f):
    sheet.alpha_composite(im.resize((im.width * f, im.height * f), Image.NEAREST), (x, y))


def tile(sheet, d, im, x, y, label, sub, accent):
    """4x on checker, 1x on navy, 1x on light, 32 px (filtered like the game's downscale)."""
    checker(d, x, y, 256, 256)
    paste_scaled(sheet, im, x, y, 4)
    d.rectangle([x + 264, y, x + 264 + 79, y + 79], fill=NAVY)
    sheet.alpha_composite(im, (x + 264 + 8, y + 8))
    d.rectangle([x + 264, y + 88, x + 264 + 79, y + 88 + 79], fill=LIGHTBG)
    sheet.alpha_composite(im, (x + 264 + 8, y + 96))
    d.rectangle([x + 264, y + 176, x + 264 + 79, y + 176 + 79], fill=NAVY)
    sheet.alpha_composite(im.resize((32, 32), Image.LANCZOS), (x + 264 + 24, y + 176 + 24))
    d.text((x, y + 264), label, font=font(20), fill=accent)
    d.text((x, y + 290), sub, font=font(13), fill=DIM)


def header(d, w, title, lines, accent):
    d.text((24, 18), title, font=font(30), fill=accent)
    for i, s in enumerate(lines):
        d.text((24, 60 + 20 * i), s, font=font(14), fill=TXT)
    y = 60 + 20 * len(lines) + 10
    d.rectangle([16, y, w - 16, y + 2], fill=accent)
    return y + 14


def slot_row(sheet, d, ims, x, y, caption):
    d.text((x, y), caption, font=font(14), fill=TXT)
    y += 22
    for i, im in enumerate(ims):
        sx = x + i * 76
        d.rectangle([sx, y, sx + 71, y + 71], fill=(28, 40, 62), outline=(64, 84, 118))
        sheet.alpha_composite(im, (sx + 4, y + 4))
    return y + 80


def sheet_sigils(ims):
    W, H = 1180, 1080
    sh = Image.new("RGBA", (W, H), PAGE + (255,))
    d = ImageDraw.Draw(sh)
    y = header(d, W, "RARITY SIGILS - DRAFT v1 (64 x 64 item icons)", [
        "Skyy 2026-10-12: rarity-upgrade items are SIGILS, one per rarity, on any gear with a rarity, skip tiers, upward only (docs/answered/gear.md).",
        "One family: a hex plate with a recessed field and a glowing UP ARROW in the rarity colour (tools/skyyui.py RARITY). The frame grows with rank:",
        "iron -> gold -> rose gold + rivets + bar -> platinum + top gem -> blackened steel + gold blades -> obsidian + gold crown + 2 gems.",
        "Frame metals Normal..Legendary = the approved accessory-icon metals (iron, gold, rose gold, platinum). Normal is drawn for completeness only.",
    ], (238, 189, 76))
    for i, (name, col, _, _) in enumerate(RAR):
        x = 24 + (i % 3) * 384
        yy = y + (i // 3) * 330
        sub = "Skyy_Sigil_%s   rarity %s%s" % (name, col, "" )
        tile(sh, d, ims[i], x, yy, "%s Sigil%s" % (name, " (optional)" if name == "Normal" else ""), sub, glow_ramp(col)[4] if name != "Normal" else TXT)
    slot_row(sh, d, ims, 24, y + 670, "In inventory slots (1x, menu navy):")
    d.text((24, y + 790), "Smithing mock:  [Normal Pickaxe]  +  [Legendary Sigil]  ->  Legendary Pickaxe   (skips Unique + Rare)",
           font=font(15), fill=TXT)
    sh.alpha_composite(ims[3], (24, y + 816))
    d.text((96, y + 838), "= the sigil you use decides the NEW rarity, whatever the old one was (upward only).", font=font(14), fill=DIM)
    return sh.convert("RGB")


def sheet_shards(hub, portals):
    W, H = 1560, 1000
    sh = Image.new("RGBA", (W, H), PAGE + (255,))
    d = ImageDraw.Draw(sh)
    y = header(d, W, "HUB SHARD + SHARD PORTALS - DRAFT v1 (64 x 64 item icons)", [
        "One family = the same hex crystal shard: faceted rim, a portal SWIRL in its window, a cream symbol in the swirl. Colour = which shard.",
        "Hub Shard (mini-boss drop, opens the portal to the hub; research/Tutorial-Plan.md): a LOOSE void-violet shard in a gold key clasp, gold compass",
        "star inside (= the SkyWynn menu emblem's star). Shard Portals (docs/answered/skills.md 2026-10-11): the same shard PLANTED in a little floating",
        "island (a shard is a portal to a mini island) - right-click opens the shard menu. Mining / Foraging / Farming / Ranching / Orchard / Combat.",
    ], (148, 102, 238))
    allims = [("Hub Shard", "Skyy_Hub_Shard   void violet " + VOID, hub, crystal_ramp(VOID)[5])]
    for i, (sid, lab, col, kind) in enumerate(SHARDS):
        allims.append(("%s Shard Portal" % lab, "Skyy_Shard_Portal_%s   %s   symbol: %s" % (sid, col, kind), portals[i],
                       crystal_ramp(col)[5]))
    for i, (lab, sub, im, acc) in enumerate(allims):
        x = 24 + (i % 4) * 384
        yy = y + (i // 4) * 330
        tile(sh, d, im, x, yy, lab, sub, acc)
    slot_row(sh, d, [a[2] for a in allims], 24, y + 670, "Hotbar / inventory slots (1x):")
    return sh.convert("RGB")


def sheet_nexus(n128, n64):
    W, H = 1500, 900
    sh = Image.new("RGBA", (W, H), PAGE + (255,))
    d = ImageDraw.Draw(sh)
    y = header(d, W, "NEXUS OF THE VOID - DRAFT v1 (128 x 128 emblem + 64 x 64 icon)", [
        "research/Rebirth-Ideas.md: the rebirth tree RADIATES from a black hole in the centre; touching it, the void imprints your soul.",
        "Drawn: the hole (deepest void violet, never pure black) + a bright photon ring, a spiral accretion swirl (ember near the hole, violet out),",
        "8 radiating branches with nodes (inner lit = spent, outer dim = to come), and a cyan SOUL being pulled into the hole along one arm.",
        "The 128 is the hover / click button at the centre of /rebirth; the 64 is for a menu tile or an item icon.",
    ], (160, 126, 224))
    checker(d, 24, y, 512, 512)
    paste_scaled(sh, n128, 24, y, 4)
    d.text((24, y + 520), "128 x 128 at 4x", font=font(15), fill=TXT)
    x = 560
    d.rectangle([x, y, x + 143, y + 143], fill=(10, 10, 18))
    sh.alpha_composite(n128, (x + 8, y + 8))
    d.text((x, y + 150), "128 at 1x on a dark page", font=font(13), fill=DIM)
    d.rectangle([x + 160, y, x + 160 + 143, y + 143], fill=LIGHTBG)
    sh.alpha_composite(n128, (x + 168, y + 8))
    d.text((x + 160, y + 150), "128 at 1x on light", font=font(13), fill=DIM)
    checker(d, x, y + 180, 256, 256)
    paste_scaled(sh, n64, x, y + 180, 4)
    d.text((x, y + 442), "64 x 64 at 4x (fewer branches)", font=font(15), fill=TXT)
    d.rectangle([x + 272, y + 180, x + 272 + 79, y + 180 + 79], fill=NAVY)
    sh.alpha_composite(n64, (x + 280, y + 188))
    d.rectangle([x + 272, y + 268, x + 272 + 79, y + 268 + 79], fill=LIGHTBG)
    sh.alpha_composite(n64, (x + 280, y + 276))
    d.rectangle([x + 272, y + 356, x + 272 + 79, y + 356 + 79], fill=NAVY)
    sh.alpha_composite(n64.resize((32, 32), Image.LANCZOS), (x + 296, y + 380))
    # mock: the centre of the /rebirth page (the emblem with tree lines continuing outward)
    mx, my, mw = 1000, y, 476
    d.rectangle([mx, my, mx + mw, my + mw], fill=(12, 10, 22))
    cxm, cym = mx + mw // 2, my + mw // 2
    for b in range(8):
        a = math.radians(-90 + b * 45)
        for j, rr in enumerate((110, 150, 190)):
            px_, py_ = cxm + rr * math.cos(a), cym + rr * math.sin(a)
            qx, qy = cxm + (rr - 34) * math.cos(a), cym + (rr - 34) * math.sin(a)
            d.line([qx, qy, px_, py_], fill=LINE[3] if j == 0 else LINE[2], width=3)
            r = 9 if j < 2 else 7
            d.rectangle([px_ - r, py_ - r, px_ + r, py_ + r], fill=(EMBER[4] if j == 0 and b % 2 == 0 else LINE[3]),
                        outline=OUTLINE)
    sh.alpha_composite(n128.resize((256, 256), Image.NEAREST), (cxm - 128, cym - 128))
    d.text((mx, my + mw + 8), "Mock: /rebirth centre (node squares = placeholder tree, not a design)", font=font(13), fill=DIM)
    return sh.convert("RGB")


# ------------------------------------------------------------------ main
def save(im, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path, "PNG", optimize=False)


def check_icon(im, name):
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            assert a in (0, 255), (name, "soft alpha", x, y)
            if a:
                assert (r, g, b) not in ((0, 0, 0), (255, 255, 255)), (name, "pure black / white", x, y)


def main():
    out = {}
    sig = []
    for i, (name, _, _, _) in enumerate(RAR):
        im = sigil(i).image()
        sig.append(im)
        out["Skyy_Sigil_%s" % name] = im
    hub = hub_shard().image()
    out["Skyy_Hub_Shard"] = hub
    portals = []
    for i, (sid, _, _, _) in enumerate(SHARDS):
        im = shard_portal(i).image()
        portals.append(im)
        out["Skyy_Shard_Portal_%s" % sid] = im
    n128 = nexus(128).image()
    n64 = nexus(64).image()
    out["Skyy_Nexus_Of_The_Void"] = n128
    out["Skyy_Nexus_Of_The_Void_64"] = n64
    manifest = {"note": "drafts for Skyy's review; ids PROPOSED, UNVERIFIED against Assets.zip / pack mods", "files": {}}
    for k, im in out.items():
        check_icon(im, k)
        p = os.path.join(ICONS, k + ".png")
        save(im, p)
    sheets = {"sheet-sigils.png": sheet_sigils(sig), "sheet-shards.png": sheet_shards(hub, portals),
              "sheet-nexus.png": sheet_nexus(n128, n64)}
    for k, im in sheets.items():
        save(im, os.path.join(HERE, k))
    for root in (ICONS, HERE):
        for fn in sorted(os.listdir(root)):
            if fn.endswith(".png"):
                fp = os.path.join(root, fn)
                with open(fp, "rb") as fh:
                    data = fh.read()
                im = Image.open(fp)
                manifest["files"][os.path.relpath(fp, HERE).replace(os.sep, "/")] = {
                    "size": list(im.size), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    with open(os.path.join(HERE, "manifest.json"), "w", newline="\n") as fh:
        json.dump(manifest, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("wrote %d icons + %d sheets" % (len(out), len(sheets)))


if __name__ == "__main__":
    main()
