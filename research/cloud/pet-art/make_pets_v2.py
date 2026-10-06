#!/usr/bin/env python3
"""SkyWynn Pets v2 - concept sheet in a vanilla-Hytale-like "voxel model" look
(cloud draft 2026-10-06).

Skyy's review of v1 (docs/answered/pets.md, 2026-10-06): "i dont really like any
accept maybe the rabbit. more drtail, and match the hytale style/look".

So v2 does not paint flat side-view sprites any more. Every pet is BUILT like a
Hytale creature model - a handful of boxes (cuboids: head, body, legs, ears ...),
each with its own hand-painted-style texture (fur noise, painted gradient,
bevel highlights, eyes, nose, spots) at roughly one texel per model unit - and
then RENDERED with a tiny software ray-caster in a 3/4 view onto a 128 x 128
"model icon" canvas (the vanilla model icon size), lit from the top-left, with a
1-px dark outline. Shown at 2x (sheet) and 3x (per-pet files).

Original art only: no game files, no copied models or textures (vanilla or
any mod). Python + Pillow only. Deterministic: same code -> same bytes.

Run:   python3 research/cloud/pet-art/make_pets_v2.py            (all files)
       python3 research/cloud/pet-art/make_pets_v2.py rabbit wolf  (preview
       only those pets into ./preview-v2.png next to the script - delete it after)
"""
import math
import os
import sys
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__))
CANVAS = 128                 # vanilla model icon size (UNVERIFIED: 128 x 128)
SHEET_SCALE = 2
SOLO_SCALE = 3

# ---------------------------------------------------------------- small math
def hx(s):
    s = s.lstrip('#')
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def mul(a, k):
    return (a[0] * k, a[1] * k, a[2] * k)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def norm(a):
    n = math.sqrt(dot(a, a))
    return (a[0] / n, a[1] / n, a[2] / n)


def mmul(m, v):          # m = rows
    return (dot(m[0], v), dot(m[1], v), dot(m[2], v))


def mtmul(m, v):         # transpose(m) * v
    return (m[0][0] * v[0] + m[1][0] * v[1] + m[2][0] * v[2],
            m[0][1] * v[0] + m[1][1] * v[1] + m[2][1] * v[2],
            m[0][2] * v[0] + m[1][2] * v[1] + m[2][2] * v[2])


def mm(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)) for i in range(3))


def rotm(axis, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    if axis == 'x':
        return ((1, 0, 0), (0, c, -s), (0, s, c))
    if axis == 'y':
        return ((c, 0, s), (0, 1, 0), (-s, 0, c))
    return ((c, -s, 0), (s, c, 0), (0, 0, 1))


def hsh(*a):
    """deterministic hash -> 0..1"""
    h = 2166136261
    for v in a:
        h ^= int(v) & 0xffffffff
        h = (h * 16777619) & 0xffffffff
        h ^= h >> 13
        h = (h * 0x5bd1e995) & 0xffffffff
        h ^= h >> 15
    return h / 4294967296.0


def mix(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)


# ---------------------------------------------------------------- the model
FACES = {(0, 1): '+x', (0, -1): '-x', (1, 1): '+y', (1, -1): '-y', (2, 1): '+z', (2, -1): '-z'}


class Box:
    """One cuboid of a creature model. Units = texels (x forward, y up, z = the
    side that faces the camera). c = centre, s = size, col = base colour,
    rot = [(axis, degrees), ...] about `pivot` (default: centre),
    tex = surface style, deco = [fn(face, tx, ty, tz, box) -> colour|None]."""
    _n = 0

    def __init__(self, c, s, col, rot=(), pivot=None, tex='fur', deco=(), grad=0.14, noise=1.0):
        Box._n += 1
        self.id = Box._n
        self.c, self.s = c, s
        self.h = (s[0] / 2, s[1] / 2, s[2] / 2)
        self.col = hx(col) if isinstance(col, str) else col
        self.rot, self.pivot = list(rot), pivot
        self.tex, self.deco, self.grad, self.noise = tex, list(deco), grad, noise
        R = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
        for ax, dg in self.rot:
            R = mm(rotm(ax, dg), R)
        self.R = R
        pv = pivot if pivot else c
        self.cw = add(pv, mmul(R, sub(c, pv)))

    def mirror(self):
        """copy on the far side (z -> -z)"""
        rot = [(a, -d if a in 'xy' else d) for a, d in self.rot]
        pv = (self.pivot[0], self.pivot[1], -self.pivot[2]) if self.pivot else None
        b = Box((self.c[0], self.c[1], -self.c[2]), self.s, self.col, rot, pv, self.tex, self.deco,
                self.grad, self.noise)
        return b

    def corners(self):
        out = []
        for sx in (-1, 1):
            for sy in (-1, 1):
                for sz in (-1, 1):
                    out.append(add(self.cw, mmul(self.R, (sx * self.h[0], sy * self.h[1], sz * self.h[2]))))
        return out

    def hit(self, o, d):
        lo = mtmul(self.R, sub(o, self.cw))
        ld = mtmul(self.R, d)
        tmin, tmax, ax, sg = -1e9, 1e9, -1, 0
        for i in range(3):
            h = self.h[i]
            if abs(ld[i]) < 1e-12:
                if abs(lo[i]) > h:
                    return None
                continue
            t1 = (-h - lo[i]) / ld[i]
            t2 = (h - lo[i]) / ld[i]
            s = -1
            if t1 > t2:
                t1, t2, s = t2, t1, 1
            if t1 > tmin:
                tmin, ax, sg = t1, i, s
            tmax = min(tmax, t2)
            if tmin > tmax:
                return None
        p = add(lo, mul(ld, tmin))
        return tmin, ax, sg, p


def sym(*boxes):
    """near-side boxes + their mirrored far-side copies"""
    out = []
    for b in boxes:
        out += [b, b.mirror()]
    return out


# ---------------------------------------------------------------- camera + light
AZ, EL = 34.0, 24.0                         # 3/4 view from front-left of the animal, a bit above
_ca, _sa = math.cos(math.radians(AZ)), math.sin(math.radians(AZ))
_ce, _se = math.cos(math.radians(EL)), math.sin(math.radians(EL))
TOCAM = norm((_sa * _ce, _se, _ca * _ce))    # from target to camera
RIGHT = norm(cross(mul(TOCAM, -1), (0, 1, 0)))
UP = cross(RIGHT, mul(TOCAM, -1))
LIGHT = norm(add(add(mul(UP, 1.0), mul(RIGHT, -0.75)), mul(TOCAM, 0.55)))   # top-left, a bit frontal


def tone(rgb, b):
    """painterly shade: cool, slightly purple shadows; warm highlights"""
    if b < 1.0:
        k = 1.0 - b
        dark = (rgb[0] * b * 0.95, rgb[1] * b * 0.95, rgb[2] * b * 1.02 + 8 * k)
        return dark
    k = min(1.0, (b - 1.0))
    return mix(rgb, (255, 246, 214), k * 0.85)


# surface styles: brightness offset per texel
def tex_offset(box, face, tx, ty, tz):
    i = box.id
    t = box.tex
    n1 = hsh(i, tx, ty, tz, 7) - 0.5
    n2 = hsh(i, tx // 2, ty // 2, tz // 2, 3) - 0.5
    if t == 'fur':        # streaky painted fur: vertical-ish strokes
        st = hsh(i, tx, tz, ty // 3, 11) - 0.5
        return 0.07 * n1 + 0.06 * n2 + 0.05 * st
    if t == 'wool':       # soft round clumps
        cx, cy = (tx + (ty // 3) % 2 * 2) % 4, ty % 3
        if face in ('+y', '-y'):
            cx, cy = (tx + (tz // 3) % 2 * 2) % 4, tz % 3
        bump = 0.10 if (cx, cy) in ((1, 0), (2, 0)) else (-0.10 if cy == 2 and cx in (0, 3) else 0.0)
        return bump + 0.05 * n1 + 0.04 * n2
    if t == 'feather':    # overlapping feather rows
        row = ty % 4 if face not in ('+y', '-y') else tx % 4
        edge = 0.09 if row == 3 else (-0.08 if row == 0 else 0.0)
        return edge + 0.05 * n1 + 0.03 * n2
    if t == 'scale':      # dragon scales: little arches
        ox = (ty // 2) % 2
        u = (tx + ox) % 3 if face not in ('+x', '-x') else (tz + ox) % 3
        v = ty % 2 if face not in ('+y', '-y') else tz % 2
        if face in ('+y', '-y'):
            u = (tx + (tz // 2) % 2) % 3
        e = 0.06 if (v == 0 and u == 1) else (-0.05 if (v == 1 and u != 1) else 0.0)
        return e + 0.04 * n1
    if t == 'horn':       # growth rings
        L = max(range(3), key=lambda a: box.s[a])
        ring = (tx, ty, tz)[L] % 3
        return (0.09 if ring == 0 else (-0.07 if ring == 2 else 0.0)) + 0.03 * n1
    if t == 'leather':
        return 0.04 * n1 + 0.04 * n2
    if t == 'smooth':
        return 0.03 * n1 + 0.03 * n2
    return 0.0


def shade_texel(box, face, tx, ty, tz, n):
    col = box.col
    for fn in box.deco:
        r = fn(face, tx, ty, tz, box)
        if r is not None:
            if r == 'skip':
                continue
            col = hx(r) if isinstance(r, str) else r
            break
    # soft, even "model icon" light from the top-left: top brightest, the
    # near side (+z) next, the front (+x) and underside darker
    b = 0.88 + 0.20 * n[1] + 0.10 * n[2] - 0.10 * n[0]
    # painted vertical gradient: darker toward the bottom of each part (baked AO)
    sy = box.s[1]
    if face in ('+y',):
        b += 0.06
    elif face == '-y':
        b -= 0.12
    else:
        rel = (ty + 0.5) / max(1.0, sy)
        b -= box.grad * (1.0 - rel) * 0.8
        if ty >= int(sy) - 1:          # bevel highlight on the top edge
            b += 0.07
        elif ty == 0:
            b -= 0.05
    # bevel on the vertical edges of side faces
    if face in ('+z', '-z') and (tx == 0 or tx >= int(box.s[0]) - 1):
        b -= 0.04
    b += tex_offset(box, face, tx, ty, tz) * box.noise
    b = round(b * 20) / 20.0           # pixel-art banding
    return tone(col, b)


# ---------------------------------------------------------------- render
BG = hx('#b4b9bf')
BG_SHADOW = hx('#9ba1a8')


def render(boxes, fit=112, hover=0.0, margin_bottom=10, shadow=True):
    """ray-cast the boxes into a CANVAS x CANVAS RGBA image (fit to `fit` px)"""
    pts = [p for b in boxes for p in b.corners()]
    sx = [dot(p, RIGHT) for p in pts]
    sy = [dot(p, UP) for p in pts]
    w, h = max(sx) - min(sx), max(sy) - min(sy)
    zoom = min(fit / w, (fit - 4) / h)
    cx = (max(sx) + min(sx)) / 2
    top_y = max(sy)
    # place: centred horizontally, bottom near the canvas bottom
    by = min(sy)
    off_y = CANVAS - margin_bottom - (top_y - by) * zoom    # top row of the model

    def to_world(px, py):
        u = cx + (px + 0.5 - CANVAS / 2) / zoom
        v = top_y - (py + 0.5 - off_y) / zoom
        return add(add(mul(RIGHT, u), mul(UP, v)), mul(TOCAM, 500))

    def to_screen(p):
        return ((dot(p, RIGHT) - cx) * zoom + CANVAS / 2, off_y + (top_y - dot(p, UP)) * zoom)

    # screen bbox per box
    bbs = []
    for b in boxes:
        cs = [to_screen(p) for p in b.corners()]
        bbs.append((max(0, int(min(c[0] for c in cs)) - 1), min(CANVAS - 1, int(max(c[0] for c in cs)) + 1),
                    max(0, int(min(c[1] for c in cs)) - 1), min(CANVAS - 1, int(max(c[1] for c in cs)) + 1)))
    ray = mul(TOCAM, -1)
    depth = [[1e9] * CANVAS for _ in range(CANVAS)]
    ids = [[0] * CANVAS for _ in range(CANVAS)]
    cols = [[None] * CANVAS for _ in range(CANVAS)]
    for b, (x0, x1, y0, y1) in zip(boxes, bbs):
        for py in range(y0, y1 + 1):
            for px in range(x0, x1 + 1):
                r = b.hit(to_world(px, py), ray)
                if not r:
                    continue
                t, ax, sg, p = r
                if t >= depth[py][px]:
                    continue
                n = mmul(b.R, tuple(sg if i == ax else 0 for i in range(3)))
                txl = []
                for i in range(3):
                    v = p[i] + b.h[i]
                    if i == ax:
                        v = 0 if sg < 0 else b.s[i] - 0.5
                    txl.append(min(int(b.s[i] - 1e-6), max(0, int(math.floor(v)))))
                depth[py][px] = t
                ids[py][px] = b.id
                cols[py][px] = shade_texel(b, FACES[(ax, sg)], txl[0], txl[1], txl[2], n)
    img = Image.new('RGBA', (CANVAS, CANVAS), (0, 0, 0, 0))
    px_ = img.load()
    for y in range(CANVAS):
        for x in range(CANVAS):
            c = cols[y][x]
            if c is None:
                continue
            # inner line: this part sits behind its upper/left neighbour part
            for dx, dy in ((-1, 0), (0, -1), (1, 0), (0, 1)):
                X, Y = x + dx, y + dy
                if 0 <= X < CANVAS and 0 <= Y < CANVAS and ids[Y][X] and ids[Y][X] != ids[y][x] \
                        and depth[Y][X] < depth[y][x] - 1.2:
                    c = mul(c, 0.62)
                    break
            px_[x, y] = (int(max(0, min(255, c[0]))), int(max(0, min(255, c[1]))),
                         int(max(0, min(255, c[2]))), 255)
    # outer 1-px outline: a dark version of the neighbouring colour
    out = img.copy()
    po = out.load()
    for y in range(CANVAS):
        for x in range(CANVAS):
            if px_[x, y][3]:
                continue
            nb = [px_[X, Y] for X, Y in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))
                  if 0 <= X < CANVAS and 0 <= Y < CANVAS and px_[X, Y][3]]
            if nb:
                c = nb[0]
                po[x, y] = (int(c[0] * 0.28) + 8, int(c[1] * 0.26) + 6, int(c[2] * 0.30) + 10, 255)
    # ground shadow (under everything)
    ground = [p for b in boxes for p in b.corners()]
    gx = [p[0] for p in ground]
    gz = [p[2] for p in ground]
    feet = [to_screen((x, 0.0, z)) for x in (min(gx), max(gx)) for z in (min(gz), max(gz))]
    fx0, fx1 = min(f[0] for f in feet), max(f[0] for f in feet)
    fy0, fy1 = min(f[1] for f in feet), max(f[1] for f in feet)
    shrink = 0.25 if hover else 0.0
    wdt = (fx1 - fx0) * (0.42 - shrink)
    mx, my = (fx0 + fx1) / 2, (fy0 + fy1) / 2
    base = Image.new('RGBA', (CANVAS, CANVAS), (0, 0, 0, 0))
    if shadow:
        ImageDraw.Draw(base).ellipse((mx - wdt, my - (fy1 - fy0) * 0.30 - 1, mx + wdt, my + (fy1 - fy0) * 0.30 + 1),
                                     fill=BG_SHADOW + (255,))
    base.alpha_composite(out)
    return base


# ---------------------------------------------------------------- decal helpers
def eye(cx, cy, w=5, h=5, iris='#5a3418', face='+z', lid=None, glint=True):
    """Big expressive Hytale-ish eye painted on a side face. (cx, cy) = texel of
    its lower-left corner (y counts up from the bottom). Dark rim, coloured iris,
    tall pupil looking forward, a 2 x 2 white glint top-left, a small lighter
    reflection bottom-right, optional lid line above."""
    irisc = hx(iris)
    pup = (16, 12, 14)
    rim = (34, 24, 22)
    big = w >= 5

    def fn(face_, tx, ty, tz, box):
        if face_ not in (face, '-z' if face == '+z' else face):
            return None
        u, v = tx - cx, ty - cy
        if not (0 <= u < w and 0 <= v < h):
            if lid and -1 <= u <= w and v == h:
                return hx(lid) if isinstance(lid, str) else lid
            return None
        top = h - 1
        if glint and big and (u, v) in ((1, top - 1), (2, top - 1), (1, top - 2)):
            return (255, 255, 252)
        if glint and not big and w >= 4 and (u, v) == (1, top - 1):
            return (255, 255, 252)
        if glint and w < 4 and (u, v) == (0, top):
            return (255, 255, 252)
        if v == 0 or u == 0 or u == w - 1 or v == top:
            if big and (u, v) in ((0, 0), (w - 1, 0), (0, top), (w - 1, top)):
                return 'skip'
            return rim
        if big and (u, v) == (w - 2, 1):
            return mix(irisc, (255, 255, 255), 0.45)
        if u >= w - 3 and v >= 1 and u <= w - 2 and v <= top - 1 and (w >= 4):
            return pup if u == w - 3 or v >= 2 else irisc
        return irisc
    return fn


def patch(face_set, x0, y0, x1, y1, col, z0=None, z1=None):
    """solid colour patch in texel coords (inclusive) on the given faces"""
    c = hx(col) if isinstance(col, str) else col
    fs = set(face_set.split(',')) if isinstance(face_set, str) else set(face_set)

    def fn(face, tx, ty, tz, box):
        if face not in fs:
            return None
        if x0 <= tx <= x1 and y0 <= ty <= y1 and (z0 is None or z0 <= tz <= z1):
            return c
        return None
    return fn


def belly(rows, col, faces='+z,-z,+x,-x,-y'):
    """lower `rows` texel rows in a lighter colour, with a ragged painted edge"""
    c = hx(col)
    fs = set(faces.split(','))

    def fn(face, tx, ty, tz, box):
        if face not in fs:
            return None
        if face == '-y':
            return c
        edge = rows + (1 if hsh(box.id, tx, tz, 5) > 0.6 else 0) - (1 if hsh(box.id, tx, tz, 9) > 0.8 else 0)
        return c if ty < edge else None
    return fn


def tip(rows, col, faces='+z,-z,+x,-x,+y'):
    """top `rows` rows in another colour (ear tips, socks, horns)"""
    c = hx(col)
    fs = set(faces.split(','))

    def fn(face, tx, ty, tz, box):
        if face not in fs:
            return None
        if face == '+y':
            return c
        return c if ty >= int(box.s[1]) - rows else None
    return fn


def bottom(rows, col, faces='+z,-z,+x,-x,-y'):
    """lowest rows in another colour (hooves, paws, socks)"""
    c = hx(col)
    fs = set(faces.split(','))

    def fn(face, tx, ty, tz, box):
        if face not in fs:
            return None
        return c if (face == '-y' or ty < rows) else None
    return fn


def front_face(col, x_rows=None):
    c = hx(col)

    def fn(face, tx, ty, tz, box):
        return c if face == '+x' else None
    return fn


def speckle(col, p=0.12, seed=1, faces='+z,-z,+y,+x,-x'):
    c = hx(col)
    fs = set(faces.split(','))

    def fn(face, tx, ty, tz, box):
        if face in fs and hsh(seed, box.id, tx, ty, tz) < p:
            return c
        return None
    return fn


def stripes_v(period, width, col, faces='+z,-z,+y', phase=0):
    c = hx(col)
    fs = set(faces.split(','))

    def fn(face, tx, ty, tz, box):
        if face in fs and (tx + phase + (1 if hsh(box.id, ty, 2) > 0.7 else 0)) % period < width:
            return c
        return None
    return fn


def nose_front(x0, y0, x1, y1, col, nostrils=None):
    """nose / snout pad on the front (+x) face; x = z texel (0 = far side)"""
    c = hx(col)
    k = hx(nostrils) if nostrils else None

    def fn(face, tx, ty, tz, box):
        if face != '+x':
            return None
        if k and ty == y0 + (y1 - y0) // 2 and tz in (x0 + 1, x1 - 1):
            return k
        if x0 <= tz <= x1 and y0 <= ty <= y1:
            return c
        return None
    return fn


def mouth_side(x0, x1, y, col='#3a2418'):
    c = hx(col)

    def fn(face, tx, ty, tz, box):
        if face in ('+z', '-z') and ty == y and x0 <= tx <= x1:
            return c
        return None
    return fn


# ---------------------------------------------------------------- the pets
# Proportions follow the (UNVERIFIED) vanilla Hytale creature look described in
# the README: big boxy heads, compact bodies, short thick legs, large eyes with a
# white glint, warm natural colours, painted gradients + subtle texture noise.

def rabbit():
    fur, cream, dark, back = '#b48a5e', '#f0e4cc', '#7e5a3c', '#9a7450'
    pink = '#e8a2a2'
    spk = speckle('#a67c52', 0.10, 2)
    body = Box((-1, 10, 0), (19, 12, 13), fur, rot=[('z', 8)], deco=[belly(4, cream), patch('+y', 0, 0, 30, 30, back, 4, 8), spk])
    rump = Box((-7, 9.5, 0), (10, 15, 15), fur, deco=[belly(4, cream), patch('+y', 0, 0, 30, 30, back, 5, 9), spk])
    head = Box((10, 16, 0), (13, 12, 13), fur,
               deco=[eye(5, 5, 5, 5, '#6a3a1c', lid=dark),
                     patch('+z,-z', 9, 0, 12, 2, cream), patch('+z,-z', 10, 3, 12, 3, cream),
                     patch('+z,-z', 3, 2, 4, 3, cream),
                     patch('+x', 0, 0, 12, 2, cream),
                     patch('+x', 0, 3, 12, 4, '#d8c4a6', 4, 8),
                     patch('+y', 0, 0, 30, 30, back, 5, 7),
                     speckle('#a67c52', 0.10, 4, faces='+y,+z,-z')])
    cheek = Box((16.8, 13, 0), (3, 5, 9), cream, grad=0.05,
                deco=[patch('+x', 0, 3, 9, 4, pink, 3, 5), patch('+x', 0, 2, 9, 2, '#c49a8a', 4, 4),
                      patch('+x', 0, 0, 9, 0, '#8a6a52', 4, 4)])
    ear = Box((7.5, 27.5, 3.4), (3, 13, 4.6), fur, rot=[('z', 16), ('x', 12)], pivot=(7.5, 21.5, 3.4),
              deco=[tip(2, dark), bottom(1, back), patch('+z', 1, 1, 1, 9, pink), patch('+z', 1, 2, 1, 8, '#f4c0bc'),
                    patch('-z', 0, 1, 2, 10, back)])
    hind = Box((-6, 6.5, 6.2), (10, 10, 3), fur, deco=[belly(3, cream, faces='+z,-z,+x,-x'), spk])
    foot = Box((-2.5, 1.2, 6), (12, 2.4, 3.6), cream, grad=0.04,
               deco=[patch('+z,-z,+x', 9, 0, 11, 2, '#dccbb0'), patch('+x', 0, 0, 0, 3, '#cdb89a', 1, 1)])
    fleg = Box((6.5, 4, 3.4), (3, 8, 3), fur, deco=[bottom(3, cream)])
    tail = Box((-13, 13, 0), (5, 5, 6), '#f6f2ea', tex='wool', grad=0.08)
    return [body, rump, head, cheek, tail] + sym(ear, hind, foot, fleg)


def chicken():
    white, cream = '#f2ede2', '#d9cdb6'
    red, beak = '#c8362c', '#e8a630'
    body = Box((0, 13, 0), (18, 13, 14), white, tex='feather', deco=[belly(3, cream)])
    breast = Box((8, 13, 0), (5, 11, 12), white, tex='feather')
    tailb = Box((-10, 20, 0), (5, 12, 8), white, tex='feather', rot=[('z', 22)], pivot=(-8, 15, 0),
                deco=[tip(3, '#e0d6c4')])
    head = Box((11, 25, 0), (9, 10, 9), white, tex='feather',
               deco=[eye(4, 4, 3, 3, '#c26018'), patch('+z,-z', 7, 1, 8, 4, red)])
    comb = Box((10.5, 31, 0), (7, 4, 3), red, tex='smooth',
               deco=[patch('+z,-z', 1, 3, 1, 3, '#e86050'), patch('+z,-z', 4, 3, 4, 3, '#e86050')])
    bk = Box((17, 25, 0), (4, 3, 4), beak, tex='smooth', deco=[patch('+z,-z', 0, 0, 3, 0, '#b07418')])
    wattle = Box((15.5, 21, 0), (2.5, 4, 3), red, tex='smooth')
    wing = Box((-1, 13.5, 7.4), (12, 8, 1.2), '#e4dccd', tex='feather',
               deco=[stripes_v(3, 1, '#cfc4b0', faces='+z,-z')])
    leg = Box((1.5, 3.5, 3), (2, 7, 2), beak, tex='smooth')
    foot = Box((3, 0.6, 3), (6, 1.2, 4), beak, tex='smooth')
    return [body, breast, tailb, head, comb, bk, wattle] + sym(wing, leg, foot)


def goat():
    coat, light, horn = '#e9e2d4', '#f7f2e8', '#9c8466'
    body = Box((0, 17, 0), (28, 15, 15), coat, deco=[belly(4, '#d6ccb8'), speckle('#d8cfbf', 0.12, 3)])
    neck = Box((12, 22, 0), (8, 12, 10), coat, rot=[('z', -20)])
    head = Box((17, 28, 0), (11, 11, 10), coat,
               deco=[eye(3, 4, 5, 5, '#d8a020', lid='#a89c88'), nose_front(3, 1, 6, 4, '#b8a898', '#3c3028'),
                     patch('+z,-z', 9, 0, 10, 3, '#d8ccba')])
    snout = Box((23.5, 25.5, 0), (4, 6, 7), coat, deco=[nose_front(1, 2, 5, 4, '#c0a8a0', '#40302c'),
                                                       mouth_side(0, 3, 1)])
    beard = Box((21.5, 19.5, 0), (4, 7, 4), '#d9d0c0', tex='wool', rot=[('z', -8)])
    horn1 = Box((16, 36.5, 2.8), (2.8, 7, 2.8), horn, tex='horn', rot=[('z', 20)], pivot=(16, 33, 2.8))
    horn1b = Box((14.4, 42, 2.8), (2.2, 7, 2.2), horn, tex='horn', rot=[('z', 20), ('z', 38)], pivot=(16, 33, 2.8),
                 deco=[tip(2, '#d8c6a8')])
    ear = Box((14.5, 31, 6.5), (5, 2, 4), coat, rot=[('x', -25)], deco=[patch('+y', 0, 0, 9, 9, '#e6b8a8')])
    leg = Box((9, 6, 4.5), (4, 12, 4), coat, deco=[bottom(3, '#3a3430')])
    leg2 = Box((-9, 6, 4.5), (4, 12, 4), coat, deco=[bottom(3, '#3a3430')])
    tail = Box((-15, 23, 0), (3, 5, 4), coat, rot=[('z', 30)])
    return [body, neck, head, snout, beard, tail] + sym(horn1, horn1b, ear, leg, leg2)


def _hog(hide, mane, tusk, paint=False, warts=True, big=1.0):
    """shared rig for Warthog / Tusker (different looks, one body plan)"""
    k = big
    deco = [belly(4, mix_hex(hide, '#000000', 0.15)), speckle(mix_hex(hide, '#000000', 0.22), 0.10, 5)]
    if paint:
        deco = [stripes_v(6, 1, '#eae2d2', faces='+z,-z', phase=2)] + deco
    body = Box((0, 13 * k, 0), (28 * k, 15 * k, 16 * k), hide, deco=deco)
    shoulder = Box((9 * k, 15 * k, 0), (10 * k, 17 * k, 17 * k), hide, deco=deco[-2:])
    head = Box((17 * k, 13 * k, 0), (12 * k, 13 * k, 13 * k), hide,
               deco=[eye(5, 6, 4, 4, '#e0a030' if paint else '#6a3a1c', lid=mix_hex(hide, '#000000', 0.3)),
                     speckle(mix_hex(hide, '#000000', 0.22), 0.10, 6)])
    snout = Box((24.5 * k, 10 * k, 0), (5 * k, 7 * k, 9 * k), mix_hex(hide, '#d89a8a', 0.35),
                deco=[nose_front(2, 2, 6, 5, '#d8a294', '#3a2020')])
    tuskb = Box((25 * k, 13.5 * k, 5 * k), (2, 6 * k, 2), tusk, tex='horn', rot=[('z', -25)],
                pivot=(25 * k, 10 * k, 5 * k), deco=[tip(2, '#fff8e8')])
    out = [body, shoulder, head, snout] + sym(tuskb)
    if warts:
        out += sym(Box((22.5 * k, 14 * k, 6.8 * k), (3, 3, 1.5), mix_hex(hide, '#000000', 0.12)))
    bristle = stripes_v(2, 1, mix_hex(mane, '#ffffff', 0.22), faces='+z,-z,+y,+x,-x')
    out.append(Box((-2 * k, 21.5 * k, 0), (22 * k, 3, 5), mane, deco=[bristle]))
    out.append(Box((9 * k, 24.5 * k, 0), (11 * k, 4, 5.5), mane, rot=[('z', -6)], deco=[bristle]))
    out.append(Box((15.5 * k, 21.5 * k, 0), (4, 4, 5), mane, deco=[bristle]))
    ear = Box((14 * k, 22.5 * k, 5 * k), (4, 5, 2), hide, rot=[('x', -30), ('z', 15)],
              deco=[patch('+z', 1, 1, 2, 3, '#c88a7a')])
    leg = Box((8 * k, 4 * k, 5 * k), (5 * k, 8 * k, 5 * k), hide, deco=[bottom(2, '#2a2420')])
    leg2 = Box((-9 * k, 4 * k, 5 * k), (5 * k, 8 * k, 5 * k), hide, deco=[bottom(2, '#2a2420')])
    tail = Box((-15 * k, 16 * k, 0), (2, 8, 2), hide, rot=[('z', -25)], deco=[bottom(3, mane)])
    return out + [tail] + sym(ear, leg, leg2)


def mix_hex(a, b, t):
    c = mix(hx(a), hx(b), t)
    return '#%02x%02x%02x' % tuple(int(v) for v in c)


def warthog():
    return _hog('#8e8a86', '#4e4640', '#efe6cf')


def tusker():
    return _hog('#a8492a', '#d4442a', '#f2d06a', paint=True, big=1.0)


def bear():
    fur, muz = '#7a5234', '#c8a07a'
    body = Box((0, 17, 0), (30, 20, 22), fur, deco=[belly(4, '#5e3e26'), speckle('#6a4630', 0.12, 3)])
    hump = Box((7, 25, 0), (12, 8, 18), fur, deco=[speckle('#8c6444', 0.14, 4)])
    head = Box((19, 21, 0), (14, 14, 15), fur,
               deco=[eye(8, 7, 4, 4, '#4a2a14', lid='#4a2e1c'), speckle('#6a4630', 0.10, 6)])
    snout = Box((27.5, 17.5, 0), (5, 7, 8), muz, deco=[nose_front(2, 3, 5, 6, '#2a2020', None),
                                                        mouth_side(0, 4, 1, '#5a4030')])
    ear = Box((17, 29.5, 5.5), (4, 4, 3.5), fur, deco=[patch('+z', 1, 0, 2, 2, '#c8a07a')])
    leg = Box((10, 6, 7), (7, 12, 7), fur, deco=[bottom(2, '#3e2818')])
    leg2 = Box((-9, 6, 7), (7, 12, 7), fur, deco=[bottom(2, '#3e2818')])
    claw = Box((14, 0.8, 7), (2, 1.6, 6), '#e8dcc4', tex='horn')
    tail = Box((-16, 22, 0), (3, 4, 4), fur)
    return [body, hump, head, snout, tail] + sym(ear, leg, leg2, claw)


def turkey():
    brown, red, blue = '#6e4a30', '#c43424', '#7ab2d4'
    fan = []
    cols = ['#5a3a22', '#8a5a34', '#b07a44', '#7a4c2c']
    for i, a in enumerate(range(-60, 61, 20)):
        fan.append(Box((-9, 26, 0), (2, 22, 6), cols[i % 4], tex='feather', rot=[('x', a)], pivot=(-9, 16, 0),
                       deco=[tip(3, '#e8d8b8', faces='+z,-z,-x,+x'),
                             tip(5, '#2a1a10', faces='+x,-x,+z,-z')]))
    body = Box((0, 14, 0), (18, 15, 15), brown, tex='feather', deco=[stripes_v(3, 1, '#4e3220', faces='+z,-z')])
    wing = Box((-1, 15, 7.8), (13, 9, 1.4), '#8e6a46', tex='feather', deco=[tip(2, '#d8c8a8', faces='-z,+z')])
    neck = Box((9, 22, 0), (4, 9, 4), blue, tex='smooth', deco=[speckle('#e05a4a', 0.2, 7)])
    head = Box((10.5, 28, 0), (6, 6, 5), blue, tex='smooth', deco=[eye(2, 2, 2, 2, '#3a2010', glint=True)])
    bk = Box((14.5, 28, 0), (3, 2, 2), '#e0b860', tex='smooth')
    snood = Box((14.5, 24.5, 0), (2, 5, 2), red, tex='smooth')
    wattle = Box((11.5, 23, 0), (3, 5, 3), red, tex='smooth')
    leg = Box((1.5, 3.5, 3), (2, 7, 2), '#c86a50', tex='smooth')
    foot = Box((3, 0.6, 3), (6, 1.2, 4), '#c86a50', tex='smooth')
    return fan + [body, neck, head, bk, snood, wattle] + sym(wing, leg, foot)


def wolf():
    grey, light, dark = '#8c939c', '#dfe2e4', '#4e555e'
    body = Box((0, 17, 0), (28, 13, 13), grey, deco=[belly(4, light), speckle(dark, 0.08, 2)])
    chest = Box((10, 18, 0), (9, 15, 15), grey, deco=[belly(6, light, faces='+x,+z,-z,-y'),
                                                       patch('+x', 0, 0, 20, 20, light)])
    ruff = Box((6, 24.5, 0), (8, 5, 14), dark, deco=[speckle(grey, 0.2, 3)])
    head = Box((18, 24, 0), (11, 11, 11), grey,
               deco=[eye(5, 5, 4, 3, '#e0b030', lid=dark), patch('+z,-z', 0, 0, 10, 2, light)])
    snout = Box((25, 21, 0), (6, 5, 6), light, deco=[tip(2, grey, faces='+z,-z,+y'),
                                                     patch('+x', 0, 3, 9, 4, '#22262a', 2, 3),
                                                     mouth_side(0, 5, 0, '#3a3e44')])
    ear = Box((16.5, 31.5, 3.2), (4, 6, 2.5), grey, rot=[('z', -6)],
              deco=[patch('+z', 1, 0, 2, 3, '#c8a8a0'), tip(2, dark)])
    leg = Box((10, 6, 4.5), (4, 12, 4), grey, deco=[bottom(2, light)])
    leg2 = Box((-10, 6, 4.5), (4, 12, 4), grey, deco=[bottom(2, light)])
    tail = Box((-18, 16, 0), (12, 5, 5), grey, rot=[('z', 35)], pivot=(-13, 20, 0),
               deco=[patch('+z,-z,+y,-y,-x', 0, 0, 3, 9, light)])
    return [body, chest, ruff, head, snout, tail] + sym(ear, leg, leg2)


def boar():
    hide, mane = '#5e4030', '#2e2018'
    out = _hog(hide, mane, '#efe2c4', warts=False)
    return out


def hawk():
    brown, cream, dark = '#7a5434', '#ecdcbc', '#4a3020'
    body = Box((0, 16, 0), (14, 16, 12), brown, tex='feather', rot=[('z', 18)],
               deco=[patch('+x', 0, 0, 20, 20, cream), speckle('#b08a60', 0.15, 4, faces='+x')])
    breast = Box((4.5, 14, 0), (5, 13, 10), cream, tex='feather', rot=[('z', 14)],
                 deco=[stripes_v(3, 1, '#b48a5c', faces='+z,-z,+x')])
    head = Box((6, 28, 0), (10, 9, 9), brown, tex='feather',
               deco=[eye(5, 3, 3, 3, '#e8b020', lid=dark), patch('+z,-z', 6, 0, 9, 2, cream)])
    brow = Box((8.5, 31.3, 0), (5, 1.6, 9.6), dark, tex='smooth')
    bk = Box((12, 27.5, 0), (3, 3, 3.5), '#e8c040', tex='smooth')
    hook = Box((14, 26.5, 0), (2.4, 3.4, 2.4), '#34343a', tex='smooth', deco=[tip(1, '#5a5a62')])
    wing = Box((-3, 16, 6.8), (16, 13, 1.6), brown, tex='feather', rot=[('z', 24)],
               deco=[stripes_v(4, 1, dark, faces='+z,-z'), tip(4, '#9a724a', faces='+z,-z')])
    tail = Box((-11, 8, 0), (10, 2, 8), dark, tex='feather', rot=[('z', 40)],
               deco=[stripes_v(3, 1, '#c8a878', faces='+y,-y,+z,-z')])
    perch = Box((3, 2, 0), (22, 4, 5), '#6a4a30', tex='horn',
                 deco=[patch('+x,-x', 0, 0, 9, 9, '#c8a878'), speckle('#4a3020', 0.12, 9)])
    leg = Box((3, 6, 2.5), (2, 4, 2), '#e8b830', tex='smooth')
    return [perch, body, breast, head, brow, bk, hook, tail] + sym(wing, leg)


def _sheep(fleece, face_col, hornc, horn_big=True, saddle_on=False, coat_tex='wool'):
    body = Box((0, 17, 0), (28, 17, 18), fleece, tex=coat_tex, grad=0.16,
               deco=[speckle(mix_hex(fleece, '#000000', 0.08), 0.06, 3)])
    head = Box((17, 22, 0), (10, 11, 10), face_col,
               deco=[eye(4, 5, 4, 3, '#c89020', lid=mix_hex(face_col, '#000000', 0.25)),
                     nose_front(3, 1, 6, 4, mix_hex(face_col, '#000000', 0.25), '#1a1414')])
    topknot = Box((15.5, 28, 0), (7, 4, 9), fleece, tex=coat_tex)
    out = [body, head, topknot]
    # curled horn: three boxes spiralling down past the eye
    h1 = Box((14.5, 28.6, 5.6), (6, 3, 3), hornc, tex='horn')
    h2 = Box((11.2, 25, 6.4), (3, 7, 3), hornc, tex='horn')
    h3 = Box((14, 21.2, 6.9), (6, 2.8, 3), hornc, tex='horn')
    h4 = Box((16.4, 23, 7.3), (2.4, 3, 2.6), hornc, tex='horn', deco=[tip(1, '#ece0c4')])
    out += sym(h1, h2, h3, h4) if horn_big else sym(h1)
    leg = Box((9, 5, 5), (4, 10, 4), face_col, deco=[bottom(2, '#2a2420')])
    leg2 = Box((-9, 5, 5), (4, 10, 4), face_col, deco=[bottom(2, '#2a2420')])
    ear = Box((14.5, 25, 6), (3, 2, 5), face_col, rot=[('x', 20)])
    out += sym(leg, leg2, ear)
    out.append(Box((-15, 20, 0), (3, 6, 4), fleece, tex=coat_tex))
    if saddle_on:
        out += saddle(-2, 26, 12, 19)
    return out


def saddle(x, y, length, width):
    """mount marker: leather saddle + gold trim + strap (original design)"""
    seat = Box((x, y, 0), (length, 3, width), '#7c3c20', tex='leather',
               deco=[tip(1, '#d4a234', faces='+z,-z,+x,-x'), speckle('#5a2a16', 0.06, 8)])
    cant = Box((x + length / 2 - 1, y + 2.5, 0), (2, 3, width - 4), '#6a321a', tex='leather',
               deco=[tip(1, '#d4a234')])
    strap = Box((x, y - 7, width / 2 + 0.3), (2, 12, 0.8), '#5a2a16', tex='leather',
                deco=[patch('+z,-z', 0, 3, 1, 4, '#f0c860')])
    return [seat, cant] + sym(strap)


def ram():
    return _sheep('#ece6da', '#4a423e', '#b8935e', horn_big=True, saddle_on=True)


def mouflon():
    out = []
    coat = '#a8643a'
    body = Box((0, 17, 0), (28, 15, 15), coat, deco=[belly(5, '#efe4d0'), patch('+z,-z', 3, 6, 9, 10, '#e8dcc4'),
                                                    speckle('#8a4e2c', 0.10, 3)])
    neck = Box((12, 22, 0), (8, 12, 10), coat, rot=[('z', -20)], deco=[belly(4, '#5a3420')])
    head = Box((17, 27, 0), (11, 10, 10), coat,
               deco=[eye(4, 5, 4, 3, '#d89a28', lid='#6a3a20'), patch('+z,-z', 8, 0, 10, 4, '#efe4d0'),
                     nose_front(3, 0, 6, 3, '#efe4d0', '#3a2a20')])
    hornc = '#9a8462'
    h1 = Box((14.5, 33.5, 4.6), (6, 3, 3), hornc, tex='horn')
    h2 = Box((11.2, 30, 5.6), (3, 7, 3), hornc, tex='horn')
    h3 = Box((14, 26.2, 6.4), (6, 2.8, 3), hornc, tex='horn', deco=[tip(1, '#d8c8a8', faces='+x,+z,-z')])
    leg = Box((9, 6, 4.5), (4, 12, 4), coat, deco=[bottom(4, '#efe4d0')])
    leg2 = Box((-9, 6, 4.5), (4, 12, 4), coat, deco=[bottom(4, '#efe4d0')])
    tail = Box((-15, 22, 0), (3, 5, 4), '#3a2418', rot=[('z', 25)])
    out = [body, neck, head, tail] + sym(h1, h2, h3, leg, leg2) + saddle(-2, 26, 12, 16)
    # priest charm: little gold sun pendant on the chest
    out.append(Box((15.5, 14.5, 0), (2, 3, 3), '#f0c860', tex='smooth'))
    return out


def horse():
    coat, mane, light = '#7a4a2a', '#2e1e14', '#efe4d0'
    body = Box((0, 24, 0), (34, 15, 15), coat, deco=[belly(3, '#5e3820'), speckle('#6a3e22', 0.08, 3)])
    neck = Box((16, 35, 0), (9, 22, 10), coat, rot=[('z', -26)], pivot=(15, 26, 0))
    head = Box((28, 42.5, 0), (16, 8, 9), coat, rot=[('z', -26)],
               deco=[eye(2, 3, 4, 4, '#4a2412', lid='#3e2414'), patch('+x', 0, 0, 9, 9, '#4a2c1c'),
                     patch('+y', 5, 0, 15, 9, light, 4, 4), patch('+z,-z', 12, 0, 15, 7, '#5a3420'),
                     patch('+z,-z', 14, 3, 14, 4, '#24140c'), mouth_side(11, 15, 1, '#2a180e')])
    mane1 = Box((10.5, 37, 0), (3.5, 22, 4), mane, rot=[('z', -26)], pivot=(15, 26, 0),
                deco=[stripes_v(2, 1, '#4a3020', faces='+z,-z,+x,-x')])
    forelock = Box((23, 48, 0), (3, 3, 4), mane)
    ear = Box((21.5, 49.5, 2.4), (2.6, 4, 2), coat, rot=[('z', -10)])
    leg = Box((12, 9, 5), (5, 18, 5), coat, deco=[bottom(4, light), bottom(1, '#2a2420')])
    leg2 = Box((-12, 9, 5), (5, 18, 5), coat, deco=[bottom(1, '#2a2420')])
    tail = Box((-20, 21, 0), (4, 18, 4), mane, rot=[('z', -22)], pivot=(-17, 30, 0),
               deco=[stripes_v(2, 1, '#4a3020', faces='+z,-z,+x,-x')])
    bridle = Box((30, 42.5, 0), (1.2, 8.4, 9.6), '#5a2a16', tex='leather', rot=[('z', -26)], pivot=(28, 42.5, 0),
                 deco=[patch('+z,-z', 0, 2, 0, 3, '#f0c860')])
    return [body, neck, head, mane1, forelock, tail, bridle] + sym(ear, leg, leg2) + saddle(1, 33, 13, 16)


def camel():
    coat, light, dark = '#c49a64', '#e8d4b0', '#8e6a40'
    body = Box((0, 24, 0), (30, 13, 15), coat, deco=[belly(3, dark), speckle('#b08854', 0.08, 3)])
    hump = Box((-2, 33, 0), (14, 7, 12), coat, deco=[tip(2, '#d8b480', faces='+y,+z,-z'),
                                                     speckle('#b08854', 0.1, 5)])
    neck = Box((18, 27, 0), (6, 16, 8), coat, rot=[('z', 40)], pivot=(15, 25, 0))
    neck2 = Box((20.5, 36, 0), (6, 11, 7), coat)
    head = Box((25, 41.5, 0), (11, 7, 7), coat,
               deco=[eye(3, 3, 3, 3, '#2a1a10', lid='#6a4a2a'), nose_front(1, 1, 5, 4, light, '#3a2a1a'),
                     mouth_side(6, 10, 1, '#6a4a2a')])
    ear = Box((21, 45.5, 2.6), (2, 2.5, 2), coat)
    leg = Box((10, 9, 4.5), (4, 18, 4), coat, deco=[bottom(3, light), patch('+z,-z,+x', 0, 10, 3, 11, dark)])
    leg2 = Box((-10, 9, 4.5), (4, 18, 4), coat, deco=[bottom(3, light), patch('+z,-z,+x', 0, 10, 3, 11, dark)])
    tail = Box((-15.5, 24, 0), (2, 9, 2), coat, rot=[('z', -12)], deco=[bottom(3, '#4a3420')])
    blanket = Box((-2, 37, 0), (18, 2.4, 16), '#b83a2c', tex='leather',
                  deco=[stripes_v(4, 2, '#e8c048', faces='+z,-z,+y'), tip(1, '#2a5a8a', faces='+z,-z')])
    tassel = Box((-2, 31.5, 8.4), (16, 3, 0.8), '#b83a2c', tex='leather',
                 deco=[stripes_v(3, 1, '#e8c048', faces='+z,-z')])
    return [body, hump, neck, neck2, head, tail, blanket] + sym(ear, leg, leg2, tassel)


def skrill():
    """original 'stormwing' (not the vanilla Skrill design): hovering little wyvern-bird"""
    body_c, belly_c, wing_c = '#2f6aa0', '#cfe6f2', '#5a3a9a'
    body = Box((0, 22, 0), (14, 10, 11), body_c, tex='feather', rot=[('z', 12)],
               deco=[belly(3, belly_c), speckle('#5a9ad0', 0.12, 3)])
    head = Box((10, 28, 0), (10, 9, 9), body_c, tex='feather',
               deco=[eye(5, 3, 4, 4, '#ffe060', lid='#1a3a60'), patch('+z,-z', 6, 0, 9, 1, belly_c)])
    bk = Box((16.5, 27, 0), (4, 3, 4), '#f0c840', tex='smooth', deco=[bottom(1, '#b08a20')])
    crest = []
    for i, (x, hgt) in enumerate(((6, 6), (8.5, 8), (11, 6))):
        crest.append(Box((x, 33 + hgt / 2, 0), (2, hgt, 2), '#ffe060', tex='smooth', rot=[('z', 25 - i * 5)],
                         pivot=(x, 32, 0), deco=[tip(2, '#ffffff')]))
    wing1 = Box((-3, 31, 6.2), (12, 14, 0.8), wing_c, tex='leather', rot=[('z', 30), ('x', 10)],
                pivot=(2, 25, 5.5), deco=[stripes_v(4, 1, '#3a2470', faces='+z,-z'), tip(1, '#9a7ae0', faces='+z,-z')])
    arm = Box((3.5, 31, 6.4), (2, 15, 2), '#1e4a76', rot=[('z', 30), ('x', 10)], pivot=(2, 25, 5.5),
              deco=[tip(2, '#ffe060')])
    tail = Box((-11, 18, 0), (12, 2.5, 2.5), body_c, rot=[('z', 25)], pivot=(-5, 21, 0))
    spark = Box((-17, 13, 0), (4, 4, 1.5), '#ffe060', tex='smooth', rot=[('z', 45)], deco=[tip(1, '#ffffff')])
    leg = Box((2, 15, 2.5), (2, 4, 2), '#f0c840', tex='smooth')
    return [body, head, bk, tail, spark] + crest + sym(wing1, arm, leg)


ELEMENTS = {   # body, belly / horn, wing membrane
    'Fire': ('#c43a20', '#f0c050', '#e07a30'),
    'Earth': ('#5a7a32', '#d8b47a', '#8a6a3a'),
    'Thunder': ('#d8b020', '#f4ecd0', '#4a5cb0'),
    'Water': ('#2a6a92', '#9ad8dc', '#3a8ab0'),
    'Air': ('#b4c8d6', '#ffffff', '#a8cce0'),
    'Blood': ('#7a1420', '#c06a6a', '#5a121a'),
    'Void': ('#3a2660', '#9a7ad0', '#281a44'),
    'Light': ('#e8d49a', '#ffffff', '#e8c060'),
    'Crystal': ('#7a72d4', '#cceaf8', '#c084e6'),
}


def dragon(element='Fire', bust=False):
    """Original juvenile dragon: chunky four-legged body, big boxy head with a
    blunt snout, swept-back horns, cheek frills, folded wings, plated belly,
    spined back and a long tapering tail. (Not Nestkeeper's model.)"""
    body_c, belly_c, wing_c = ELEMENTS[element]
    dark = mix_hex(body_c, '#000000', 0.38)
    hornc = mix_hex(belly_c, '#5a4a36', 0.40)
    bellyp = [belly(4, belly_c, faces='+z,-z,-y')]
    _pc = hx(mix_hex(belly_c, '#000000', 0.2))
    plates = lambda face, tx, ty, tz, box: _pc if face == '+x' and ty % 3 == 0 else None   # belly plates
    body = Box((0, 15, 0), (20, 13, 15), body_c, tex='scale', deco=bellyp + [patch('+y', 0, 0, 40, 40, dark, 6, 8)])
    chest = Box((9, 17, 0), (7, 14, 14), body_c, tex='scale',
                deco=[plates, patch('+x', 0, 0, 30, 30, belly_c), belly(5, belly_c, faces='+z,-z,-y')])
    neck = Box((14.5, 24, 0), (7, 11, 9), body_c, tex='scale', rot=[('z', -28)],
               deco=[patch('+x', 0, 0, 30, 30, belly_c)])
    head = Box((21, 31, 0), (14, 12, 13), body_c, tex='scale',
               deco=[eye(7, 4, 5, 5, '#ffcc30' if element != 'Void' else '#e060ff', lid=dark),
                     patch('+z,-z', 6, 9, 12, 9, dark), patch('+y', 0, 0, 40, 40, dark, 5, 7)])
    snout = Box((30.5, 28, 0), (6, 6, 10), body_c, tex='scale',
                deco=[nose_front(2, 3, 7, 4, dark, '#1a1010'), mouth_side(0, 5, 1, dark),
                      patch('+z,-z,-y', 0, 0, 5, 0, belly_c)])
    jaw = Box((26, 24.6, 0), (9, 2, 9), belly_c, tex='scale')
    fang = Box((32.5, 24.2, 3.5), (1.2, 2, 1.2), '#fff8e8', tex='smooth')
    horn = Box((16, 38.5, 4), (2.8, 12, 2.8), hornc, tex='horn', rot=[('z', 62)], pivot=(18.5, 35, 4),
               deco=[tip(3, mix_hex(hornc, '#ffffff', 0.45))])
    horn2 = Box((18.5, 38, 6.2), (2, 6, 2), hornc, tex='horn', rot=[('z', 45), ('x', 30)], pivot=(19.5, 34, 6.2),
                deco=[tip(2, mix_hex(hornc, '#ffffff', 0.45))])
    frill = Box((15, 31, 6.6), (4, 8, 1.0), wing_c, tex='leather', rot=[('z', 35)], pivot=(17, 29, 6.6),
                deco=[stripes_v(2, 1, mix_hex(wing_c, '#000000', 0.3), faces='+z,-z')])
    arm = Box((6, 30, 8), (2.6, 15, 2.6), dark, tex='scale', rot=[('z', 38), ('x', 8)], pivot=(6, 23, 7),
              deco=[tip(2, hornc)])
    memb = Box((-0.5, 29, 7.6), (12, 14, 0.9), wing_c, tex='leather', rot=[('z', 38), ('x', 8)], pivot=(6, 23, 7),
               deco=[stripes_v(3, 1, mix_hex(wing_c, '#000000', 0.32), faces='+z,-z'),
                     bottom(1, mix_hex(wing_c, '#ffffff', 0.25), faces='+z,-z')])
    leg = Box((10, 5, 5.8), (5, 10, 5), body_c, tex='scale', deco=[bottom(2, dark)])
    thigh = Box((-6, 8, 6.4), (8, 12, 5), body_c, tex='scale', deco=[bellyp[0]])
    leg2 = Box((-4.5, 2.5, 6.4), (5, 5, 5), body_c, tex='scale', deco=[bottom(2, dark)])
    toe = Box((13, 0.8, 5.8), (2, 1.6, 4.4), hornc, tex='horn')
    toe2 = Box((-1.5, 0.8, 6.4), (2, 1.6, 4.4), hornc, tex='horn')
    spines = []
    for x, y, hgt in ((-8, 21.5, 3), (-3.5, 21.5, 4), (1, 21.5, 4.5), (5.5, 22, 4)):
        spines.append(Box((x, y + hgt / 2, 0), (3, hgt, 1.6), hornc, tex='horn', rot=[('z', 28)], pivot=(x, y, 0),
                          deco=[tip(1, mix_hex(hornc, '#ffffff', 0.4))]))
    tail1 = Box((-13, 12, 1), (9, 8, 9), body_c, tex='scale', rot=[('z', 10), ('y', 12)], deco=bellyp)
    tail2 = Box((-18, 7, 5), (8, 6, 7), body_c, tex='scale', rot=[('y', 38)], deco=[belly(2, belly_c)])
    tail3 = Box((-20, 4, 10.5), (7, 4.5, 5), body_c, tex='scale', rot=[('y', 70)], deco=[belly(1, belly_c)])
    tailtip = Box((-19.5, 4, 15.5), (5, 5, 1.2), wing_c, tex='leather', rot=[('y', 90), ('x', 45)],
                  pivot=(-19.5, 4, 15.5))
    tspines = [Box((-14, 17, 1), (2.5, 3, 1.4), hornc, tex='horn', rot=[('z', 30)]),
               Box((-18, 11, 5), (2.2, 2.5, 1.4), hornc, tex='horn', rot=[('z', 30), ('y', 38)])]
    if bust:     # inventory icon: head + neck + chest + near wing, big and bold
        return [chest, neck, head, snout, jaw, spines[-1]] + sym(horn, horn2, frill, fang) + [arm, memb, leg, toe]
    return ([body, chest, neck, head, snout, jaw, tail1, tail2, tail3, tailtip] + spines + tspines +
            sym(horn, horn2, frill, arm, memb, leg, thigh, leg2, toe, toe2, fang))


# ---------------------------------------------------------------- list (same 16 as v1)
PETS = [
    ('Rabbit', rabbit, 'skill', 'Farming', 'Z1 Emerald Wilds', 'Common', False),
    ('Chicken', chicken, 'skill', 'Farming', 'Z1 Emerald Wilds', 'Common', False),
    ('Goat', goat, 'skill', 'Mining', 'Z3 Whisperfrost', 'Uncommon', False),
    ('Warthog', warthog, 'skill', 'Mining', 'Z2 Howling Sands', 'Uncommon', False),
    ('Bear', bear, 'skill', 'Foraging', 'Z3 Whisperfrost', 'Rare', False),
    ('Turkey', turkey, 'skill', 'Foraging', 'Z1 Emerald Wilds', 'Uncommon', False),
    ('Wolf', wolf, 'combat', 'Combat', 'Z3 Whisperfrost', 'Rare', False),
    ('Boar', boar, 'combat', 'Combat', 'Z1 Emerald Wilds', 'Uncommon', False),
    ('Hawk', hawk, 'class', 'Archer', 'Z2 Howling Sands', 'Epic', False),
    ('Ram', ram, 'class', 'Warrior', 'Z3 Whisperfrost', 'Epic', True),
    ('Skrill', skrill, 'class', 'Mage', 'Z4 Devastated Lands', 'Epic', False),
    ('Tusker', tusker, 'class', 'Berserker', 'Z4 Devastated Lands', 'Epic', False),
    ('Mouflon', mouflon, 'class', 'Priest', 'Z2 Howling Sands', 'Epic', True),
    ('Horse', horse, 'mount', 'Mount', 'Z2 Howling Sands (stable)', 'Uncommon', True),
    ('Camel', camel, 'mount', 'Mount', 'Z2 Howling Sands', 'Rare', True),
    ('Dragon Hatchling', dragon, 'dragon', 'Combat, flies at Lv 10', 'Z5 dinosaur caves', 'Mythic', True),
]
HOVER = {'Skrill'}

ROWS = [
    ('Skill pets  (slot 1: buffs only, never fight)', ['skill']),
    ('Combat + class pets  (Summon slot: fight on foot)', ['combat', 'class']),
    ('Mounts  (Summon slot, Zone 2 stable quest) + the dragon', ['mount', 'dragon']),
]

RARITY = {
    'Common': hx('#e8e8e8'), 'Uncommon': hx('#3fbf3f'), 'Rare': hx('#4060e0'),
    'Epic': hx('#a030c8'), 'Legendary': hx('#f0a018'), 'Mythic': hx('#ff4ad2'),
}
INK = (34, 36, 40)
SUB = (60, 64, 70)


# ---------------------------------------------------------------- output
def font(n):
    return ImageFont.load_default(size=n)


def icon(name, fn):
    boxes = fn()
    return render(boxes, fit=112 if name not in ('Horse', 'Camel') else 118, hover=name in HOVER)


def on_bg(img):
    base = Image.new('RGBA', img.size, BG + (255,))
    base.alpha_composite(img)
    return base


def card(img, s, name, role, zone, rarity, mount, n=22):
    big = on_bg(img).resize((CANVAS * s, CANVAS * s), Image.NEAREST)
    pad = 66
    out = Image.new('RGBA', (big.width, big.height + pad), BG + (255,))
    out.paste(big, (0, 0))
    d = ImageDraw.Draw(out)
    d.rectangle((10, big.height + 2, big.width - 11, big.height + 7), fill=RARITY[rarity], outline=(40, 42, 46))
    title = name + ('  [mount]' if mount and 'Dragon' not in name else '')
    d.text((big.width // 2, big.height + 11), title, font=font(n), fill=INK, anchor='mt')
    d.text((big.width // 2, big.height + 35), f'{role}  |  {rarity}', font=font(14), fill=SUB, anchor='mt')
    d.text((big.width // 2, big.height + 51), zone, font=font(13), fill=SUB, anchor='mt')
    return out


def save(im, name, colors=256):
    im = im.convert('RGB').quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(os.path.join(OUT, name), optimize=True)


def element_strip(cols=5, s=1):
    names = list(ELEMENTS)
    cw, ch = CANVAS * s, CANVAS * s + 20
    rows = (len(names) + cols - 1) // cols
    out = Image.new('RGBA', (cols * cw, rows * ch), BG + (255,))
    d = ImageDraw.Draw(out)
    for i, el in enumerate(names):
        x, y = (i % cols) * cw, (i // cols) * ch
        im = on_bg(render(dragon(el), fit=112)).resize((cw, cw), Image.NEAREST)
        out.paste(im, (x, y))
        d.text((x + cw // 2, y + cw + 2), el + (' (secret)' if i >= 5 else ''), font=font(13),
               fill=INK if i < 5 else SUB, anchor='mt')
    return out


def dragon_icons():
    """inventory icon concept: 128 x 128 model icon + 64 x 64 item icon size"""
    im128 = render(dragon('Fire'), fit=124, margin_bottom=(CANVAS - 124) // 2 + 8, shadow=False)
    plate = Image.new('RGBA', (CANVAS, CANVAS), (0, 0, 0, 0))
    plate.alpha_composite(im128)
    im64 = plate.resize((64, 64), Image.LANCZOS)
    return plate, im64


def preview(names):
    ims = []
    for name, fn, *_ in PETS:
        if name.lower().split()[0] in names:
            ims.append(on_bg(icon(name, fn)).resize((CANVAS * 3, CANVAS * 3), Image.NEAREST))
    sheet = Image.new('RGB', (len(ims) * CANVAS * 3, CANVAS * 3), BG)
    for i, im in enumerate(ims):
        sheet.paste(im, (i * CANVAS * 3, 0))
    sheet.save(os.path.join(OUT, 'preview-v2.png'))


def main():
    if len(sys.argv) > 1:
        preview([a.lower() for a in sys.argv[1:]])
        return
    icons, cards = {}, {}
    for name, fn, fam, role, zone, rar, mount in PETS:
        icons[name] = icon(name, fn)
        cards[name] = card(icons[name], SHEET_SCALE, name, role, zone, rar, mount)
        save(card(icons[name], SOLO_SCALE, name, role, zone, rar, mount, n=28),
             'pet-' + name.lower().replace(' ', '-') + '-v2.png', colors=200)
    strip = element_strip()
    save(strip, 'dragon-elements-v2.png')
    d128, d64 = dragon_icons()
    d128.save(os.path.join(OUT, 'icon-dragon-128-v2.png'), optimize=True)
    d64.save(os.path.join(OUT, 'icon-dragon-64-v2.png'), optimize=True)

    cw, chh = next(iter(cards.values())).size
    gap, top, head = 14, 64, 30
    ncol = 7
    sheet_w = ncol * cw + (ncol + 1) * gap
    rows_h = [head + chh + gap for _ in ROWS]
    sheet_h = top + sum(rows_h) + 40
    sheet = Image.new('RGBA', (sheet_w, sheet_h), BG + (255,))
    d = ImageDraw.Draw(sheet)
    d.text((sheet_w // 2, 16), 'SkyWynn Pets v2 - Hytale-style voxel model concepts (cloud draft)',
           font=font(32), fill=INK, anchor='mt')
    y = top
    for title, fams in ROWS:
        d.text((gap, y + 4), title, font=font(18), fill=SUB)
        y += head
        row = [p for p in PETS if p[2] in fams]
        for i, p in enumerate(row):
            x = gap + i * (cw + gap)
            if p[2] == 'dragon':
                d.rectangle((x - 5, y - 5, x + cw + 4, y + chh + 2), outline=RARITY['Mythic'], width=3)
            sheet.paste(cards[p[0]], (x, y))
        if 'dragon' in fams:
            x = gap + len(row) * (cw + gap) + 10
            d.text((x, y - 2), 'Dragon - 9 elements (recolours of one model)', font=font(15), fill=INK)
            sheet.paste(strip, (x, y + 18))
            ix = x + strip.width + 24
            d.text((ix, y - 2), 'Inventory icon', font=font(15), fill=INK)
            d.text((ix, y + 16), '128 x 128 (left, at 1x) + 64 x 64 (2x)', font=font(13), fill=SUB)
            sheet.paste(on_bg(d128), (ix, y + 36))
            sheet.paste(on_bg(d64).resize((128, 128), Image.NEAREST), (ix + CANVAS + 12, y + 36))
            d.text((ix, y + 36 + CANVAS + 8), 'Original design "in the spirit" of the', font=font(13), fill=SUB)
            d.text((ix, y + 36 + CANVAS + 24), 'Nestkeeper dragons - NOT their model.', font=font(13), fill=SUB)
            d.text((ix, y + 36 + CANVAS + 40), 'Render from their model only after', font=font(13), fill=SUB)
            d.text((ix, y + 36 + CANVAS + 56), "Aures' OK (asked 2026-10-06).", font=font(13), fill=SUB)
        y += chh + gap
    x = gap
    for r, col in RARITY.items():
        d.rectangle((x, y + 4, x + 26, y + 16), fill=col, outline=(40, 42, 46))
        d.text((x + 32, y + 3), r, font=font(14), fill=INK)
        x += 130
    d.text((x + 20, y + 3), 'Rendered from box models (Hytale-like) at 128 x 128, shown 2x. Zones + rarities '
           'are proposals.', font=font(14), fill=SUB)
    save(sheet, 'pet-sheet-v2.png')


if __name__ == '__main__':
    main()
