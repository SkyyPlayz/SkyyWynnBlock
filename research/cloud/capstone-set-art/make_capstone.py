#!/usr/bin/env python3
"""SkyWynn capstone sets - concept art (cloud draft 2026-10-06, v2 detail level).

The three Set-rarity sets from research/cloud/Capstone-Sets.md, each in its
Voidglass (F1-F4) and Aetherium (F5-F7) version, front + back:
  The Bailiff's Plate   (Heavy: Helmet, Chest, Boots)
  The Clerk's Leathers  (Light: Helmet, Chest, Legs)
  The Notary's Robes    (Cloth: Chest, Legs, Boots)

Original pixel art drawn from code (no copied art, no game files).
Run:  python3 research/cloud/capstone-set-art/make_capstone.py
Writes the PNGs next to this script. Deterministic: same code -> same bytes.

How it draws: each figure is painted on a 128 x 176 pixel grid (2x the v1
64 x 84 figures), one part at a time. Every part gets a 1-px dark outline, a
2-px lit band top-left, a 2-px shade band bottom-right and a 6-colour ramp
(outline + 5 shades), plus a material texture (brushed metal with pits and
scratches, leather grain, cloth weave, glass sheen + sparkles). Voidglass
panels are painted translucent over the part below them. The grid is scaled
up with NEAREST so the pixels stay crisp.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__))
W, H = 128, 176          # figure grid
TOP = 10                 # rows above y=0 (crest, halo)
PAD = 12                 # extra room left / right for the floating runes
CW = W + 2 * PAD         # canvas width
SCALE = 3                # 456 x 528 per figure


def hx(s):
    s = s.lstrip('#')
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def ramp(*c):
    """[outline, darkest, dark, mid, light, highlight]"""
    return [hx(x) for x in c]


# ---------------------------------------------------------------- palettes
DUMMY = ramp('#4a453f', '#77706a', '#8a8378', '#9d968a', '#b2ab9e', '#c8c1b4')
SET_G = ramp('#0b2e0b', '#1a6b1a', '#2c9a2c', '#55ff55', '#9dff9d', '#e4ffe4')   # Set rarity green
TAPE = ramp('#2a0608', '#5e1016', '#86202a', '#ab343c', '#d0585e', '#f09a9a')    # red tape ribbon
PAPER = ramp('#4a4338', '#9f9682', '#c4bba6', '#ddd5c1', '#eee8d8', '#fffdf6')
WOOD = ramp('#1f1209', '#3e2615', '#5a3a20', '#77502e', '#94683e', '#b48654')
BRASS = ramp('#3a2a0e', '#6e5019', '#9c7426', '#c79a3c', '#e6c46a', '#fbeab0')
INKC = hx('#1b1a2a')

VOID = dict(
    name='Voidglass', band='Lv 76-85 (F1-F4)',
    plate=ramp('#07050c', '#120e1c', '#1c1729', '#282038', '#3a3050', '#5a4f78'),        # dark metal
    glass=ramp('#14072c', '#2a1157', '#43208a', '#6a3cc0', '#9c70ec', '#e2d0ff'),        # violet glass
    trim=ramp('#120a20', '#3a2f52', '#5e5480', '#8a82aa', '#b8b2d2', '#ecebf8'),         # cold silver
    leather=ramp('#09080b', '#151318', '#1f1c24', '#2a2631', '#3a3543', '#524c5c'),
    cloth=ramp('#08060f', '#130f22', '#1d1734', '#282046', '#372c5e', '#4c3f7c'),
    lining=ramp('#14072c', '#2a1157', '#3b1a78', '#5a2ea8', '#7c4ed0', '#b08cf0'),
    glow=hx('#c58cff'), core=hx('#f4e8ff'), glass_alpha=0.72, runes=False)
AETH = dict(
    name='Aetherium', band='Lv 88-94 (F5-F7)',
    plate=ramp('#29324a', '#56668a', '#7a8cae', '#a0b2cf', '#c8d6ea', '#f2f8ff'),        # pale silver-blue
    glass=ramp('#1e3a5c', '#3f74a8', '#64a0d4', '#94c8ee', '#c6e6fa', '#ffffff'),        # blue-white crystal
    trim=ramp('#3a3010', '#7a6424', '#b09040', '#d8bc66', '#f0dc98', '#fff8dc'),         # pale gold
    leather=ramp('#1a2030', '#38445e', '#4c5a78', '#617092', '#7a8aac', '#98a8c8'),
    cloth=ramp('#3a4660', '#74839f', '#94a3bd', '#b3c0d6', '#d0daea', '#f2f6fc'),
    lining=ramp('#1e3a5c', '#3f74a8', '#5a92c8', '#7eb2e0', '#a8d0f2', '#e0f2ff'),
    glow=hx('#7fe8ff'), core=hx('#ffffff'), glass_alpha=0.80, runes=True)

BG = hx('#b4b9bf')
BG_SHADOW = hx('#9ca2a9')
INK = (34, 36, 40, 255)


# ---------------------------------------------------------------- noise + masks
def h01(x, y, s=0):
    n = (x * 374761393 + y * 668265263 + s * 2147483647) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65535.0


def rect(x0, y0, x1, y1):
    return {(x, y) for x in range(int(x0), int(x1) + 1) for y in range(int(y0), int(y1) + 1)}


def _draw(fn):
    im = Image.new('1', (W, H + TOP), 0)
    d = ImageDraw.Draw(im)
    fn(_Shift(d))
    px = im.load()
    return {(x, y - TOP) for x in range(W) for y in range(H + TOP) if px[x, y]}


class _Shift:
    """ImageDraw proxy that moves every shape down by TOP rows"""
    def __init__(self, d):
        self.d = d

    def _p(self, pts):
        if len(pts) == 4 and not isinstance(pts[0], tuple):
            return (pts[0], pts[1] + TOP, pts[2], pts[3] + TOP)
        return [(x, y + TOP) for x, y in pts]

    def ellipse(self, b, **k):
        self.d.ellipse(self._p(b), **k)

    def polygon(self, pts, **k):
        self.d.polygon(self._p(pts), **k)

    def line(self, pts, **k):
        self.d.line(self._p(pts), **k)


def ell(x0, y0, x1, y1):
    return _draw(lambda d: d.ellipse((x0, y0, x1, y1), fill=1))


def poly(pts):
    return _draw(lambda d: d.polygon(pts, fill=1))


def line(pts, w=1):
    return _draw(lambda d: d.line(pts, fill=1, width=w))


def mirror(m):
    return {(W - 1 - x, y) for x, y in m}


def S(m, side):
    return m if side == 0 else mirror(m)


def X(x, side):
    return x if side == 0 else W - 1 - x


def clip(m, y0=-99, y1=999, x0=-99, x1=999):
    return {(x, y) for x, y in m if y0 <= y <= y1 and x0 <= x <= x1}


def rim(m, w, side='bottom'):
    d = {'bottom': (0, 1), 'top': (0, -1), 'left': (-1, 0), 'right': (1, 0)}[side]
    return {(x, y) for x, y in m if any((x + d[0] * k, y + d[1] * k) not in m for k in range(1, w + 1))}


# ---------------------------------------------------------------- textures
def tex_metal(seed=1):
    def f(x, y, i):
        if i == 0:
            return 0
        n = h01(x, y, seed)
        if n < 0.05:
            return max(1, i - 1)            # pits
        if n > 0.965:
            return min(5, i + 1)            # glints
        if (x * 3 + y * 5 + seed) % 41 == 0 and i >= 2:
            return min(5, i + 1)            # fine scratches
        return i
    return f


def tex_leather(seed=2):
    def f(x, y, i):
        if i == 0:
            return 0
        n = h01(x, y, seed)
        if n < 0.14:
            return max(1, i - 1)
        if n > 0.93 and i < 4:
            return i + 1
        return i
    return f


def tex_cloth(seed=3):
    def f(x, y, i):
        if i == 0:
            return 0
        if (x + 2 * y) % 4 == 0 and h01(x, y, seed) < 0.6:
            return max(1, i - 1)
        if h01(x, y, seed + 7) > 0.95 and i < 5:
            return i + 1
        return i
    return f


def tex_glass(seed=4):
    def f(x, y, i):
        if i == 0:
            return 0
        d = (x + y + seed) % 23
        if d in (0, 1):
            return min(5, i + 2)            # diagonal sheen streak
        if d == 2:
            return min(5, i + 1)
        n = h01(x, y, seed)
        if n > 0.985:
            return 5                        # sparkle
        if n < 0.05:
            return max(1, i - 1)            # void speck
        return i
    return f


def tex_wax(seed=5):
    def f(x, y, i):
        if i == 0:
            return 0
        n = h01(x, y, seed)
        return max(1, i - 1) if n < 0.10 else i
    return f


# ---------------------------------------------------------------- painter
class Fig:
    def __init__(self):
        self.im = Image.new('RGBA', (W, H + TOP), (0, 0, 0, 0))
        self.px = self.im.load()

    def put(self, x, y, col, alpha=None):
        y += TOP
        if not (0 <= x < W and 0 <= y < H + TOP):
            return
        if alpha is not None:
            o = self.px[x, y]
            if o[3]:
                col = tuple(int(o[k] * (1 - alpha) + col[k] * alpha) for k in range(3)) + (255,)
        self.px[x, y] = col

    def paint(self, mask, rp, tex=None, outline=True, edge_ref=None, alpha=None, grad=True):
        mask = {p for p in mask if 0 <= p[0] < W and -TOP <= p[1] < H}
        if not mask:
            return
        ref = edge_ref if edge_ref is not None else mask
        edge = {(x, y) for x, y in mask
                if any(q not in ref for q in ((x, y - 1), (x - 1, y), (x + 1, y), (x, y + 1)))}
        inner = (mask - edge) if outline else mask
        xs = [p[0] for p in mask]
        ys = [p[1] for p in mask]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        sw, sh = max(1, x1 - x0), max(1, y1 - y0)

        def out(q):
            return q not in inner

        for (x, y) in mask:
            if outline and (x, y) in edge:
                i = 0
            else:
                up, lf = out((x, y - 1)), out((x - 1, y))
                dn, rt = out((x, y + 1)), out((x + 1, y))
                up2, lf2 = out((x, y - 2)), out((x - 2, y))
                dn2, rt2 = out((x, y + 2)), out((x + 2, y))
                if (up or lf) and (dn or rt):
                    i = 3
                elif up:
                    i = 5
                elif lf:
                    i = 4
                elif dn or rt:
                    i = 1
                elif up2 or lf2:
                    i = 4
                elif dn2 or rt2:
                    i = 2
                else:
                    i = 3
                    if grad:
                        g = (x - x0) / sw + (y - y0) / sh
                        if g > 1.45:
                            i = 2
                        elif g < 0.35:
                            i = 4
            if tex:
                i = tex(x, y, i)
            self.put(x, y, rp[i], alpha if i else None)

    def dots(self, pts, rp, alpha=None):
        for x, y, i in pts:
            self.put(int(x), int(y), rp[i], alpha)

    def col(self, pts, c):
        for x, y in pts:
            self.put(int(x), int(y), c)


# ---------------------------------------------------------------- small details
def rivet(f, x, y, rp):
    f.dots([(x, y, 5), (x + 1, y, 4), (x, y + 1, 4), (x + 1, y + 1, 2), (x + 2, y + 1, 0), (x + 1, y + 2, 0)], rp)


def stitch(f, pts, rp, i=4, every=2):
    for k, (x, y) in enumerate(pts):
        if k % every == 0:
            f.dots([(x, y, i)], rp)


def hline(x0, x1, y):
    return [(x, y) for x in range(x0, x1 + 1)]


def vline(x, y0, y1):
    return [(x, y) for y in range(y0, y1 + 1)]


def seal(f, cx, cy, r, rp=SET_G, emblem='check'):
    """green wax seal: lumpy disc, pressed ring, emblem"""
    m = ell(cx - r, cy - r, cx + r, cy + r)
    if r >= 5:
        for k in range(7):     # a few soft lumps on the edge
            a = k * 0.9 + 0.3
            bx, by = cx + math.cos(a) * (r - 0.2), cy + math.sin(a) * (r - 0.2)
            m |= ell(bx - 1.2, by - 1.2, bx + 1.2, by + 1.2)
    f.paint(m, rp, tex=tex_wax())
    if r >= 5:
        ring = ell(cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2) - ell(cx - r + 3, cy - r + 3, cx + r - 3, cy + r - 3)
        f.dots([(x, y, 1 if (x - cx) + (y - cy) > 0 else 4) for x, y in ring], rp)
    if emblem == 'check' and r >= 4:
        c = [(-2, 0), (-1, 1), (0, 2), (1, 1), (2, 0), (3, -1), (4, -2)]
        s = max(1, r // 6)
        f.dots([(cx + dx * s - 1, cy + dy * s, 1) for dx, dy in c], rp)
        f.dots([(cx + dx * s - 1, cy + dy * s - 1, 5) for dx, dy in c], rp)
    elif emblem == 'dot':
        f.dots([(cx, cy, 1), (cx - 1, cy - 1, 5)], rp)


def ribbon(f, x0, y0, x1, y1, w=4, rp=TAPE):
    """red-tape tail with a V notch at the end"""
    m = line([(x0, y0), (x1, y1)], w)
    m -= poly([(x1 - w, y1 + 1), (x1, y1 - w + 1), (x1 + w, y1 + 1)])
    f.paint(m, rp, tex=tex_cloth(9))


def tag(f, x, y, rp=PAPER, w=6, h=7):
    """paper tag (a 'filed complaint'), punched hole + tiny ink lines"""
    m = rect(x, y + 1, x + w - 1, y + h - 1) | rect(x + 1, y, x + w - 2, y)
    f.paint(m, rp, grad=False)
    f.col([(x + w // 2, y + 2)], INKC)
    f.col(hline(x + 1, x + w - 2, y + 4)[::2] + hline(x + 1, x + w - 3, y + h - 2)[::2], (90, 86, 96, 255))


FONT = {   # 3 x 5 pixel font (original)
    '0': ['111', '101', '101', '101', '111'], '1': ['010', '110', '010', '010', '111'],
    '2': ['111', '001', '111', '100', '111'], '4': ['101', '101', '111', '001', '001'],
    '6': ['111', '100', '111', '101', '111'], '7': ['111', '001', '010', '010', '010'],
    '-': ['000', '000', '111', '000', '000'], '/': ['001', '001', '010', '100', '100'],
    'B': ['110', '101', '110', '101', '110'], 'N': ['101', '111', '111', '111', '101'],
    'o': ['000', '010', '101', '010', '000'], '.': ['000', '000', '000', '000', '010'],
    ' ': ['000', '000', '000', '000', '000'],
}


def text(f, s, x, y, col):
    for ch in s:
        g = FONT[ch]
        for dy, row in enumerate(g):
            for dx, v in enumerate(row):
                if v == '1':
                    f.put(x + dx, y + dy, col)
        x += 4


RUNES = [   # original 5 x 7 glyphs
    ['01110', '10001', '00100', '01110', '00100', '10001', '01110'],
    ['10001', '01010', '00100', '11111', '00100', '01010', '10001'],
    ['00100', '01110', '10101', '00100', '10101', '01110', '00100'],
    ['11110', '10001', '10010', '11100', '10010', '10001', '11110'],
    ['01010', '01010', '11111', '01010', '11111', '01010', '01010'],
    ['00100', '01010', '10001', '11111', '10001', '01010', '00100'],
]


def rune_sprite(img, k, x, y, glow, core, scale=1):
    """floating rune on the padded canvas: soft halo + bright core"""
    g = RUNES[k % len(RUNES)]
    pts = [(x + dx, y + dy) for dy, row in enumerate(g) for dx, v in enumerate(row) if v == '1']
    px = img.load()
    halo = set()
    for (a, b) in pts:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                halo.add((a + dx, b + dy))
    for (a, b) in halo - set(pts):
        if 0 <= a < img.width and 0 <= b < img.height:
            o = px[a, b]
            base = o if o[3] else BG
            px[a, b] = tuple(int(base[c] * 0.55 + glow[c] * 0.45) for c in range(3)) + (255,)
    for (a, b) in pts:
        if 0 <= a < img.width and 0 <= b < img.height:
            px[a, b] = core if (a + b) % 3 else glow


def etched_rune(f, k, x, y, T):
    g = RUNES[k % len(RUNES)]
    for dy, row in enumerate(g):
        for dx, v in enumerate(row):
            if v == '1':
                f.put(x + dx, y + dy, T['glow'] if (dx + dy) % 2 else T['core'])


# ---------------------------------------------------------------- mannequin (free slots stay bare)
def mannequin(f, back, head=True, legs=True, feet=True):
    tx = tex_leather(11)
    if legs:
        for side in (0, 1):
            f.paint(S(rect(43, 108, 62, 162), side), DUMMY, tex=tx)
            if not back:
                f.dots([(X(52, side), y, 2) for y in (132, 133)], DUMMY)     # knee hint
    if feet:
        for side in (0, 1):
            f.paint(S(rect(41, 160, 62, 168) | rect(43, 158, 62, 160), side), DUMMY, tex=tx)
    for side in (0, 1):
        f.paint(S(rect(26, 58, 39, 122), side), DUMMY, tex=tx)              # arms
        f.paint(S(rect(26, 122, 39, 132), side), DUMMY, tex=tx)             # hands = free (Hands slot)
        f.dots([(X(x, side), y, 1) for x in (30, 33, 36) for y in (128, 129, 130, 131)], DUMMY)
    f.paint(rect(40, 54, 87, 110), DUMMY, tex=tx)                           # torso
    f.paint(rect(55, 42, 72, 56), DUMMY, tex=tx)                            # neck
    if head:
        hm = ell(46, 12, 81, 30) | rect(46, 22, 81, 40) | ell(46, 32, 81, 48)
        f.paint(hm, DUMMY, tex=tx)
        if back:
            f.dots([(x, 30, 2) for x in range(50, 78)], DUMMY)


def ground_rows():
    return 166


# ---------------------------------------------------------------- 1. The Bailiff's Plate (Heavy)
def bailiff(T, back):
    f = Fig()
    P, G, R, L = T['plate'], T['glass'], T['trim'], T['leather']
    a = T['glass_alpha']
    aeth = T['runes']
    mannequin(f, back, head=False, legs=True, feet=False)
    mt = tex_metal(21)

    # --- BOOTS: "Footnote Greaves" (knee cop, shin greave, layered sabaton)
    for side in (0, 1):
        gm = S(poly([(42, 136), (63, 136), (62, 162), (43, 162)]), side)
        f.paint(gm, P, tex=mt)
        f.paint(S(poly([(46, 140), (59, 140), (58, 156), (47, 156)]), side), G, tex=tex_glass(3 + side), alpha=a)
        if not back:   # "the small print": 4 rows of tiny engraved text on the glass
            for k, y in enumerate((143, 146, 149, 152)):
                xs = range(48, 57 - (k % 2) * 2)
                f.dots([(X(x, side), y, 5 if aeth else 4) for x in xs if h01(x, y, 5) > 0.35], G)
        else:      # calf straps
            for y in (142, 152):
                f.paint(S(rect(42, y, 63, y + 2), side), L, tex=tex_leather())
                f.dots([(X(52, side), y + 1, 5)], BRASS)
        km = S(ell(41, 126, 64, 142), side)
        f.paint(km, P, tex=mt)
        f.paint(S(ell(46, 130, 59, 139), side), G, tex=tex_glass(7), alpha=a)
        f.paint(rim(km, 2, 'bottom') & km, R, edge_ref=km)
        if not back:
            rivet(f, X(43, side) - (2 if side else 0), 133, R)
        # sabaton: ankle cuff + 3 toe lames
        sm = S(rect(40, 158, 64, 169) | rect(42, 156, 63, 158), side)
        f.paint(sm, P, tex=mt)
        for y in (160, 163, 166):
            f.dots([(X(x, side), y, 1) for x in range(41, 63)], P)
            f.dots([(X(x, side), y + 1, 4) for x in range(41, 63)], P)
        f.paint(S(rect(40, 156, 64, 158), side), R, tex=mt)
        if not back:
            seal(f, X(58, side), 152, 3, emblem='dot')          # set stamp badge (ankle)
        else:
            f.paint(S(rect(48, 166, 56, 171), side), BRASS)      # heel plate

    # --- CHEST: "Overruling Cuirass"
    torso = rect(38, 54, 89, 104) | rect(41, 52, 86, 54)
    f.paint(torso, P, tex=mt)
    if not back:
        for side in (0, 1):   # voidglass pectoral panels over the dark metal
            f.paint(S(poly([(43, 60), (60, 58), (60, 80), (47, 86), (43, 80)]), side), G, tex=tex_glass(1 + side), alpha=a)
        f.dots([(63, y, 5) for y in range(56, 100)] + [(64, y, 1) for y in range(56, 100)], P)    # keel ridge
    else:
        f.paint(poly([(56, 56), (71, 56), (68, 98), (59, 98)]), G, tex=tex_glass(6), alpha=a)     # glass spine
    # abdomen lames
    for k, y in enumerate((86, 92, 98)):
        lm = rect(39, y, 88, y + 6)
        f.paint(lm, P, tex=mt)
        f.paint(rim(lm, 1, 'bottom') & lm, R, edge_ref=lm, outline=False)
        rivet(f, 42, y + 2, R)
        rivet(f, 83, y + 2, R)
    if not back:
        # dents = filed complaints, each with a little paper tag ("all were denied")
        for dx, dy in ((47, 70), (77, 92)):
            f.dots([(dx, dy, 1), (dx + 1, dy, 1), (dx - 1, dy + 1, 1), (dx + 2, dy + 1, 4), (dx, dy + 2, 4), (dx + 1, dy + 2, 5)], P)
        f.col(line([(48, 72), (49, 76)]), (200, 196, 180, 255))
        tag(f, 47, 76)
        f.col(line([(78, 94), (80, 97)]), (200, 196, 180, 255))
        tag(f, 78, 96, w=5, h=6)
        # big green wax seal + red-tape ribbons (the set stamp)
        ribbon(f, 60, 78, 54, 102, 6)
        ribbon(f, 67, 78, 73, 101, 6)
        seal(f, 63, 74, 8 if not aeth else 9)
    else:
        # brass case plaque on the back: "27-B/6"
        # crossed red tape with a seal where it meets
        ribbon(f, 46, 58, 82, 86, 5)
        ribbon(f, 81, 58, 45, 86, 5)
        seal(f, 63, 71, 6)
        pl = rect(46, 88, 81, 99)
        f.paint(pl, BRASS, tex=tex_metal(4))
        text(f, '27-B/6', 52, 92, INKC)
        rivet(f, 47, 89, BRASS)
        rivet(f, 78, 89, BRASS)
    # wide belt + buckle
    belt = rect(37, 104, 90, 111)
    f.paint(belt, L, tex=tex_leather())
    stitch(f, hline(39, 88, 105), L, 4, 3)
    stitch(f, hline(39, 88, 110), L, 4, 3)
    if not back:
        bk = rect(57, 102, 70, 113)
        f.paint(bk, R, tex=mt)
        f.paint(rect(60, 105, 67, 110), P)
        f.dots([(63, y, 5) for y in range(105, 110)], R)
    # tassets (hip plates) over the bare thighs
    for side in (0, 1):
        tm = S(poly([(39, 111), (62, 111), (60, 126), (42, 126)]), side)
        f.paint(tm, P, tex=mt)
        f.paint(rim(tm, 2, 'bottom') & tm, G, edge_ref=tm, tex=tex_glass(2), alpha=a)
        rivet(f, X(45, side) - (2 if side else 0), 114, R)
        rivet(f, X(56, side) - (2 if side else 0), 114, R)
    if not back:   # the Bailiff's gavel on the left hip
        f.paint(rect(84, 108, 86, 128), WOOD, tex=tex_leather(5))
        gh = rect(79, 126, 92, 133)
        f.paint(gh, WOOD, tex=tex_leather(6))
        f.paint(rect(79, 126, 81, 133), BRASS)
        f.paint(rect(90, 126, 92, 133), BRASS)
    # arms: upper lames, elbow cop, vambrace (hands stay bare: the Hands slot is free)
    for side in (0, 1):
        for y in (78, 84, 90):
            um = S(rect(25, y, 40, y + 6), side)
            f.paint(um, P, tex=mt)
        em = S(ell(23, 94, 42, 110), side)
        f.paint(em, P, tex=mt)
        f.paint(S(ell(28, 98, 37, 106), side), G, tex=tex_glass(8), alpha=a)
        vm = S(poly([(25, 108), (40, 108), (42, 123), (23, 123)]), side)
        f.paint(vm, P, tex=mt)
        f.paint(rim(vm, 2, 'top') & vm, R, edge_ref=vm)
        f.paint(rim(vm, 2, 'bottom') & vm, R, edge_ref=vm)
        if not back:
            for y in (113, 116, 119):   # tally marks of the court days
                f.dots([(X(x, side), y, 4) for x in range(28, 37, 2)], G)
    # pauldrons: three layered plates, glass dome on top
    p3 = clip(ell(21, 64, 43, 90), y0=78)
    p2 = clip(ell(19, 56, 45, 82), y0=68)
    p1 = ell(16, 48, 47, 74)
    for side in (0, 1):
        for k, pm in ((3, p3), (2, p2), (1, p1)):
            pm = S(pm, side)
            f.paint(pm, P, tex=mt)
            f.paint(rim(pm, 2, 'bottom') & pm, R, edge_ref=pm)
        f.paint(S(ell(22, 52, 41, 66), side), G, tex=tex_glass(5 + side), alpha=a)
        for x in (21, 27, 33, 39):
            rivet(f, X(x, side) - (2 if side else 0), 70, R)
        if aeth and not back:
            etched_rune(f, 2 + side, X(31, side) - (4 if side else 0), 56, T)
    # gorget
    gm = poly([(42, 44), (85, 44), (89, 58), (38, 58)])
    f.paint(gm, P, tex=mt)
    f.paint(rim(gm, 2, 'top') & gm, R, edge_ref=gm)

    # --- HELMET: "Stamped Visor" (great helm, rubber-stamp crest)
    helm = ell(44, 10, 83, 34) | rect(44, 22, 83, 50)
    f.paint(helm, P, tex=mt)
    if not back:
        face = poly([(49, 24), (78, 24), (78, 46), (63.5, 52), (49, 46)])
        f.paint(face, G, tex=tex_glass(11), alpha=a)
        f.paint(rect(50, 31, 77, 34), [hx('#050308')] * 6, grad=False)          # eye slit
        for ex in (55, 56, 71, 72):
            f.put(ex, 32, T['glow'])
            f.put(ex, 33, T['core'] if ex in (55, 71) else T['glow'])
        for bx in (57, 60, 63, 66, 69):                                        # breath slots
            f.paint(rect(bx, 39, bx + 1, 45), [hx('#050308')] * 6, grad=False)
        seal(f, 49, 44, 3, emblem='dot')                                         # set stamp badge
    else:
        f.paint(rect(62, 12, 65, 50), R, tex=mt)                                 # back ridge
        f.paint(rect(48, 30, 79, 34), G, tex=tex_glass(13), alpha=a)
    brow = rect(44, 24, 83, 28)
    f.paint(brow, R, tex=mt)
    for x in range(46, 82, 6):
        rivet(f, x, 25, P)
    # rubber-stamp crest: block, stem, knob
    f.paint(rect(50, 6, 77, 12), WOOD if not aeth else T['trim'], tex=tex_leather(3))
    f.paint(rect(48, 11, 79, 14), SET_G, grad=False)                             # green ink pad edge
    f.paint(rect(61, 0, 66, 7), WOOD if not aeth else T['trim'])
    f.paint(ell(57, -6, 70, 3), BRASS if not aeth else T['glass'], tex=tex_glass(2) if aeth else None)
    if aeth:   # Chief rank: small wings either side of the stamp (echo of the vanilla Mithril helm wings)
        for side in (0, 1):
            wm = S(poly([(48, 14), (34, 2), (38, 10), (30, 6), (40, 18), (46, 20)]), side)
            f.paint(wm, T['trim'], tex=mt)
    return f


# ---------------------------------------------------------------- 2. The Clerk's Leathers (Light)
def clerk(T, back):
    f = Fig()
    P, G, R, L = T['plate'], T['glass'], T['trim'], T['leather']
    a = T['glass_alpha']
    aeth = T['runes']
    lt = tex_leather(31)
    mannequin(f, back, head=True, legs=False, feet=True)

    # --- LEGS: "Quick-Reference Trousers"
    for side in (0, 1):
        lm = S(rect(42, 106, 63, 161), side)
        f.paint(lm, L, tex=lt)
        stitch(f, S(vline(44, 112, 158), side) if side == 0 else [(127 - 44, y) for y in range(112, 159)], L, 4, 2)
        km = S(ell(42, 128, 63, 146), side)
        f.paint(km, P, tex=tex_metal(3))
        f.paint(S(ell(46, 131, 59, 143), side), G, tex=tex_glass(4 + side), alpha=a)
        f.paint(rim(km, 1, 'bottom') & km, R, edge_ref=km, outline=False)
        for y in (150, 156):                   # shin straps
            f.paint(S(rect(42, y, 63, y + 2), side), BRASS if aeth else T['trim'])
        if not back:
            # index tabs sticking out of the outer seam (green / red / blue / gold)
            for k, (yy, cc) in enumerate(((112, SET_G), (118, TAPE), (124, T['glass']), (147, BRASS))):
                f.paint(S(rect(38, yy, 42, yy + 4), side), cc, grad=False)
            if side == 0:
                seal(f, 55, 115, 3, emblem='dot')           # set stamp badge (thigh)
        else:
            pk = S(rect(46, 112, 59, 124), side)            # back pocket stuffed with receipts
            f.paint(S(rect(48, 108, 52, 114), side), PAPER, grad=False)
            f.paint(S(rect(53, 109, 56, 114), side), PAPER, grad=False)
            f.paint(pk, L, tex=lt)
            stitch(f, [(x, y) for x, y in rim(pk, 1, 'top')], L, 5, 2)

    # --- CHEST: "Filing Jerkin" (forty pockets)
    torso = rect(39, 54, 88, 110) | rect(42, 52, 85, 54)
    f.paint(torso, L, tex=lt)
    if not back:
        for side in (0, 1):
            for row, y in enumerate((60, 72, 84, 96)):
                for col_, x in enumerate((42, 51)):
                    if row == 0 and col_ == 1:
                        continue
                    xx = X(x, side) - (8 if side else 0)
                    pm = rect(xx, y, xx + 8, y + 9)
                    if (row + col_ + side) % 2 == 0:     # receipt slips poking out
                        f.paint(rect(xx + 2, y - 4, xx + 6, y + 1), PAPER, grad=False)
                        f.col([(xx + 3, y - 2), (xx + 4, y - 2), (xx + 3, y), (xx + 5, y)], (110, 106, 120, 255))
                    f.paint(pm, L, tex=lt)
                    stitch(f, vline(xx + 1, y + 4, y + 8) + vline(xx + 7, y + 4, y + 8), L, 5, 2)
                    fl = poly([(xx, y), (xx + 8, y), (xx + 8, y + 3), (xx + 4, y + 5), (xx, y + 3)])
                    f.paint(fl, R, tex=tex_metal(row))
                    f.dots([(xx + 4, y + 3, 5)], BRASS)
        # front closure with buttons, glass placket
        f.paint(rect(60, 54, 67, 110), G, tex=tex_glass(9), alpha=a)
        for y in range(60, 108, 8):
            rivet(f, 62, y, BRASS if not aeth else T['trim'])
    else:
        # scroll case across the back (rolled forms poking out) on a strap
        f.paint(line([(44, 58), (86, 104)], 5), WOOD, tex=lt)
        tube = poly([(66, 60), (74, 56), (92, 96), (84, 100)])
        f.paint(tube, P, tex=tex_metal(7))
        f.paint(poly([(68, 63), (72, 61), (88, 94), (84, 96)]), G, tex=tex_glass(3), alpha=a)
        for k in range(3):
            f.paint(ell(64 + k * 3, 50 + k, 70 + k * 3, 58 + k), PAPER)
        f.paint(poly([(64, 58), (75, 53), (77, 57), (66, 62)]), R, tex=tex_metal(5))
        seal(f, 80, 82, 4, emblem='dot')
        for y in range(62, 108, 6):
            stitch(f, hline(42, 60, y), L, 3, 3)
    # stand-up collar
    for side in (0, 1):
        cm = S(poly([(42, 44), (60, 46), (60, 56), (42, 58)]), side)
        f.paint(cm, L, tex=lt)
        f.paint(rim(cm, 2, 'top') & cm, G, edge_ref=cm, tex=tex_glass(1), alpha=a)
    # belt + ledger on the left hip
    f.paint(rect(38, 104, 89, 111), WOOD, tex=lt)
    stitch(f, hline(40, 87, 105), WOOD, 5, 2)
    if not back:
        f.paint(rect(59, 102, 68, 113), BRASS if not aeth else T['trim'], tex=tex_metal(2))
        f.paint(rect(61, 105, 66, 110), L)
        # the ledger: hard cover, page edges, bookmark ribbon
        f.col(line([(84, 111), (86, 116)]), BRASS[3])
        book = rect(80, 116, 95, 133)
        f.paint(book, G if aeth else WOOD, tex=tex_leather(8))
        f.paint(rect(93, 117, 95, 132), PAPER, grad=False)
        f.dots([(94, y, 2) for y in range(118, 132, 2)], PAPER)
        f.paint(rect(82, 118, 86, 122), T['trim'])
        f.paint(rect(88, 131, 89, 138), SET_G, grad=False)
    # arms: leather sleeves, red-tape sleeve garters, glass bracers
    for side in (0, 1):
        am = S(rect(26, 60, 39, 112), side)
        f.paint(am, L, tex=lt)
        stitch(f, S(vline(37, 64, 108), side), L, 4, 2)
        for y in ((76, 82) if aeth else (78,)):          # Senior: a second garter stripe
            f.paint(S(rect(25, y, 40, y + 3), side), TAPE, tex=tex_cloth(4))
            f.dots([(X(32, side), y + 1, 5)], BRASS)
        bm = S(poly([(25, 104), (40, 104), (41, 121), (24, 121)]), side)
        f.paint(bm, P, tex=tex_metal(9))
        f.paint(S(poly([(28, 107), (37, 107), (38, 118), (27, 118)]), side), G, tex=tex_glass(6), alpha=a)
        f.paint(rim(bm, 1, 'top') & bm, R, edge_ref=bm, outline=False)
        # shoulder pads: two layers with glass edge
        for pm in (clip(ell(19, 56, 45, 76), y0=64), poly([(24, 50), (44, 47), (47, 58), (43, 66), (21, 68), (19, 58)])):
            pm = S(pm, side)
            f.paint(pm, L, tex=lt)
            f.paint(rim(pm, 2, 'bottom') & pm, G, edge_ref=pm, tex=tex_glass(2), alpha=a)
        stitch(f, [(x, y) for x, y in S(rim(poly([(26, 53), (42, 50), (44, 58), (40, 63), (23, 64), (22, 58)]), 1, 'top'), side)], L, 5, 2)
        if aeth and not back:
            etched_rune(f, 1 + side, X(33, side) - (4 if side else 0), 56, T)

    # --- HELMET: "Eyeshade" = half-mask cowl + voidglass eyeshade, quill behind the band
    hood = ell(42, 8, 85, 40) | rect(42, 24, 85, 52)
    if not back:
        hood -= ell(49, 20, 78, 50)
    f.paint(hood, L, tex=lt)
    if not back:
        mask_ = rect(48, 39, 79, 52) | ell(48, 32, 79, 54)
        mask_ = clip(mask_, y0=39)
        f.paint(mask_, P, tex=tex_metal(12))
        for x in range(53, 76, 4):
            f.dots([(x, 46, 0), (x, 47, 0)], P)                  # breathing slits
        f.paint(rim(mask_, 1, 'top') & mask_, R, edge_ref=mask_, outline=False)
        seal(f, 74, 48, 2, emblem='dot')
    stitch(f, [(x, y) for x, y in rim(ell(44, 10, 83, 38), 1, 'top')], L, 4, 3)
    band = rect(42, 22, 85, 26)
    f.paint(band, T['trim'] if aeth else WOOD, tex=tex_leather(4))
    if not back:
        brim = poly([(40, 26), (87, 26), (82, 33), (45, 33)])
        f.paint(brim, G, tex=tex_glass(14), alpha=min(1.0, a + 0.05))
        f.paint(rect(45, 32, 82, 33), G, grad=False, alpha=0.5)
    else:
        f.paint(rect(56, 26, 71, 30), G, tex=tex_glass(15), alpha=a)       # band buckle at the back
    # the quill tucked behind the band (wearer's left)
    qm = poly([(80, 24), (96, 2), (99, 4), (84, 26)])
    f.paint(qm, PAPER if not aeth else T['glass'], tex=tex_cloth(2))
    f.col(line([(82, 26), (97, 3)]), (120, 110, 130, 255))
    f.col(line([(82, 27), (79, 32)]), INKC)
    if aeth:   # Senior rank pin on the band
        f.paint(ell(60, 20, 67, 27), T['glass'], tex=tex_glass(5))
        f.put(63, 23, T['core'])
    return f


# ---------------------------------------------------------------- 3. The Notary's Robes (Cloth)
def notary(T, back):
    f = Fig()
    P, G, R, C, Ln = T['plate'], T['glass'], T['trim'], T['cloth'], T['lining']
    a = T['glass_alpha']
    aeth = T['runes']
    ct = tex_cloth(41)
    mannequin(f, back, head=True, legs=True, feet=False)

    # --- BOOTS: "Waiting-Room Slippers" (soft, worn, a queue ticket on a loop)
    for side in (0, 1):
        sm = S(ell(38, 156, 64, 172) | rect(42, 156, 63, 165), side)
        f.paint(sm, Ln, tex=tex_cloth(5))
        cuff = S(rect(42, 154, 63, 159), side)
        f.paint(cuff, C, tex=ct)
        f.dots([(X(x, side), 157, 5) for x in range(43, 63, 2)], C)     # fluffy cuff
        if not back:
            f.dots([(X(44, side), 166, 1), (X(46, side), 167, 1)], Ln)   # worn toe
            if side == 1:
                f.col(line([(76, 159), (78, 163)]), PAPER[3])
                tk = rect(74, 162, 87, 168)
                f.paint(tk, PAPER, grad=False)
                text(f, '404', 75, 163, INKC)
            else:
                seal(f, 52, 165, 2, emblem='dot')

    # --- LEGS: "Margin Skirts" (long A-line skirts, wavy hem, red margin rule, hand-written lines)
    hem_pts = [(97 - k * 4.6, 156 + (2 if k % 2 else 0)) for k in range(15)]
    sk = poly([(40, 102), (87, 102)] + hem_pts)
    f.paint(sk, C, tex=ct)
    for x in range(44, 86, 7):                          # long folds
        f.dots([(x + (y - 102) * (x - 63) // 140, y, 1) for y in range(112, 152) if y % 3], C)
    if not back:   # split front: lining shows in the middle
        f.paint(poly([(60, 104), (67, 104), (72, 156), (55, 156)]), Ln, tex=tex_cloth(6))
    # red margin rules (one per side) and the handwriting between them
    for side in (0, 1):
        x0 = 45 if not back else 47
        f.col([(X(x0 - (y - 104) // 5, side), y) for y in range(108, 150)], TAPE[3])
    for y in range(110, 149, 5):
        for side in (0, 1):
            x0, x1 = ((48, 57) if not back else (49, 63))
            for x in range(x0 - (y - 104) // 6, x1):
                if h01(x, y, 3 + side) > 0.42:
                    f.put(X(x, side), y, C[1] if not aeth else hx('#55607a'))
    hem = clip(sk, y0=150)
    f.paint(hem, G, tex=tex_glass(8), alpha=a, edge_ref=sk)
    f.dots([(x, 152, 5) for x in range(34, 94, 4)], R)

    # --- CHEST: "Sealed Robe" (bell sleeves, mantle, high collar, glass buttons, stole, big seal)
    torso = poly([(42, 52), (85, 52), (88, 108), (39, 108)])
    f.paint(torso, C, tex=ct)
    for side in (0, 1):
        sl = S(poly([(42, 54), (24, 58), (21, 80), (12, 124), (37, 127), (41, 112), (42, 84)]), side)   # bell sleeve
        f.paint(sl, C, tex=ct)
        for k in range(3):                               # sleeve folds
            f.dots([(X(int(33 - k * 4 + (y - 70) * (0.12 + k * 0.08)), side), y, 1) for y in range(72, 118)], C)
        cuff = S(clip(sl, y0=116), side)
        f.paint(cuff, G, tex=tex_glass(3 + side), alpha=a, edge_ref=sl)
        f.paint(S(poly([(14, 125), (37, 128), (37, 130), (14, 127)]), side), Ln, grad=False)
        if aeth and not back:
            etched_rune(f, 3 + side, X(28, side) - (4 if side else 0), 96, T)
    # mantle (short capelet over both shoulders) with a scalloped glass edge
    mpts = [(38, 48), (89, 48), (97, 70)]
    for k in range(9):
        mpts.append((97 - k * 7.5 - 3.7, 74 if k % 2 == 0 else 70))
    mpts.append((30, 70))
    mantle = poly(mpts)
    if not back:
        mantle -= poly([(56, 46), (71, 46), (66, 76), (61, 76)])
    f.paint(mantle, C, tex=ct)
    f.paint(clip(mantle, y0=68), G, tex=tex_glass(12), alpha=a, edge_ref=mantle)
    stitch(f, [(x, 66) for x in range(34, 94)], R, 4, 2)
    if not back:
        f.paint(rect(60, 56, 67, 106), Ln, tex=tex_cloth(7))          # front placket
        for y in range(60, 104, 8):                                   # glass buttons
            f.paint(ell(61, y, 66, y + 5), G, tex=tex_glass(y))
            f.put(62, y + 1, G[5])
        for side in (0, 1):                                           # the stole with stamps
            st = S(poly([(48, 52), (56, 52), (56, 112), (48, 116)]), side)
            f.paint(st, Ln if not aeth else T['glass'], tex=tex_cloth(8))
            for y in range(60, 110, 12):
                f.paint(S(rect(49, y, 54, y + 5), side), SET_G if (y // 12) % 2 else R, grad=False)
                f.dots([(X(51, side), y + 2, 5)], SET_G if (y // 12) % 2 else R)
        ribbon(f, 70, 78, 74, 100, 4)
        ribbon(f, 74, 78, 80, 98, 3)
        seal(f, 73, 72, 7)
        # sash with a quill and an inkpot
        f.paint(rect(38, 100, 89, 106), R if aeth else TAPE, tex=tex_cloth(4))
        f.paint(rect(43, 106, 49, 113), P, tex=tex_metal(2))          # inkpot
        f.paint(rect(44, 104, 48, 106), [hx('#050308')] * 6, grad=False)
        f.col(line([(46, 104), (40, 88)]), PAPER[4])
        f.col(line([(45, 104), (39, 89)]), PAPER[2])
    else:
        # embroidered Department seal across the back + queue number
        f.paint(ell(46, 60, 81, 95), Ln, tex=tex_cloth(9))
        ring = ell(48, 62, 79, 93) - ell(51, 65, 76, 90)
        f.dots([(x, y, 4 if (x + y) % 3 else 5) for x, y in ring], R)
        seal(f, 63, 77, 7)
        f.paint(rect(38, 100, 89, 106), R if aeth else TAPE, tex=tex_cloth(4))
        f.paint(rect(56, 98, 71, 108), R if aeth else TAPE, tex=tex_cloth(5))       # sash knot
        ribbon(f, 60, 106, 56, 128, 4, R if aeth else TAPE)
        ribbon(f, 67, 106, 71, 126, 4, R if aeth else TAPE)
    # standing collar (tall for the High Notary)
    tall = 6 if aeth else 0
    for side in (0, 1):
        cm = S(poly([(44, 38 - tall), (61, 46), (61, 58), (42, 56)]), side)
        f.paint(cm, C, tex=ct)
        f.paint(rim(cm, 2, 'top') & cm, R, edge_ref=cm)
        f.paint(S(poly([(46, 42 - tall), (58, 48), (58, 54), (45, 52)]), side), G, tex=tex_glass(10), alpha=a)
    if aeth:   # High rank: a floating seal halo behind / above the head
        ring = ell(42, -2, 85, 14) - ell(46, 1, 81, 11)
        for x, y in ring:
            f.put(x, y, T['glow'] if (x + y) % 4 else T['core'])
    return f


# ---------------------------------------------------------------- output
SETS = [
    ('bailiff', bailiff, ("The Bailiff's Plate", "The Chief Bailiff's Plate"), 'Heavy',
     'Helmet + Chest + Boots (Legs free)'),
    ('clerk', clerk, ("The Clerk's Leathers", "The Senior Clerk's Leathers"), 'Light',
     'Helmet + Chest + Legs (Boots free)'),
    ('notary', notary, ("The Notary's Robes", "The High Notary's Robes"), 'Cloth',
     'Chest + Legs + Boots (Helmet free)'),
]
RUNE_SPOTS = [(2, 40), (139, 30), (1, 98), (141, 92), (3, 140), (139, 148)]


def font(n):
    return ImageFont.load_default(size=n)


def render(fig, T, seed):
    """figure grid -> padded canvas (runes) -> scaled image on the sheet background"""
    can = Image.new('RGBA', (CW, H + TOP), (0, 0, 0, 0))
    can.alpha_composite(fig.im, (PAD, 0))
    if T['runes']:
        for k, (x, y) in enumerate(RUNE_SPOTS):
            rune_sprite(can, k + seed, x, y + TOP + (seed % 3) * 2, T['glow'], T['core'])
    big = can.resize((CW * SCALE, (H + TOP) * SCALE), Image.NEAREST)
    base = Image.new('RGBA', big.size, BG)
    d = ImageDraw.Draw(base)
    d.ellipse(((PAD + 30) * SCALE, (166 + TOP) * SCALE, (PAD + 97) * SCALE, (175 + TOP) * SCALE), fill=BG_SHADOW)
    base.alpha_composite(big)
    return base


def label(im, title, sub, n=22):
    pad = 50
    out = Image.new('RGBA', (im.width, im.height + pad), BG)
    out.paste(im, (0, 0))
    d = ImageDraw.Draw(out)
    d.text((im.width // 2, im.height + 4), title, font=font(n), fill=INK, anchor='mt')
    d.text((im.width // 2, im.height + 30), sub, font=font(14), fill=(60, 64, 70, 255), anchor='mt')
    return out


def save(im, name, colors=200):
    im = im.convert('RGB').quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(os.path.join(OUT, name), optimize=True)


def main():
    cells = {}
    for key, fn, names, typ, slots in SETS:
        for ti, T in enumerate((VOID, AETH)):
            fr = render(fn(T, False), T, 0)
            bk = render(fn(T, True), T, 1)
            cells[(key, ti)] = (fr, bk)
            pair = Image.new('RGBA', (fr.width * 2 + 16, fr.height), BG)
            pair.paste(fr, (0, 0))
            pair.paste(bk, (fr.width + 16, 0))
            d = ImageDraw.Draw(pair)
            d.text((10, 8), 'front', font=font(16), fill=INK)
            d.text((fr.width + 26, 8), 'back', font=font(16), fill=INK)
            d.rectangle((pair.width - 30, 8, pair.width - 12, 26), fill=SET_G[3], outline=SET_G[0])
            save(label(pair, f'{names[ti]} ({T["name"]}, {typ})', f'{T["band"]}  |  {slots}  |  Set rarity  |  concept, cloud draft'),
                 f'{key}-{T["name"].lower()}.png')

    fw, fh = cells[('bailiff', 0)][0].size
    gap, top, labh = 18, 96, 56
    sheet_w = 4 * fw + 5 * gap
    sheet_h = top + 3 * (fh + labh + gap) + 10
    sheet = Image.new('RGBA', (sheet_w, sheet_h), BG)
    d = ImageDraw.Draw(sheet)
    d.text((sheet_w // 2, 16), "SkyWynn capstone sets - the Department's issued uniforms (concept, cloud draft v2)",
           font=font(34), fill=INK, anchor='mt')
    d.text((sheet_w // 2, 58), 'Set rarity (green) - drops only in The Final Audit.  Columns: Voidglass front / back, Aetherium front / back.  '
           'Bare grey mannequin parts = the free 4th slot (and the Hands slot).', font=font(17), fill=(60, 64, 70, 255), anchor='mt')
    for r, (key, fn, names, typ, slots) in enumerate(SETS):
        y = top + r * (fh + labh + gap)
        for c in range(4):
            ti, view = c // 2, c % 2
            x = gap + c * (fw + gap)
            sheet.paste(cells[(key, ti)][view], (x, y))
            T = (VOID, AETH)[ti]
            t1 = names[ti] + ('' if view == 0 else ' (back)')
            d.text((x + fw // 2, y + fh + 6), t1, font=font(22 if view == 0 else 18), fill=INK, anchor='mt')
            d.text((x + fw // 2, y + fh + 32), f'{T["name"]} {typ}  |  {T["band"]}', font=font(14),
                   fill=(60, 64, 70, 255), anchor='mt')
            if view == 0:
                sw = [T['glass'][3], T['plate'][3], T['trim'][3], SET_G[3]]
                for j, col in enumerate(sw):
                    d.rectangle((x + 8 + j * 18, y + 8, x + 22 + j * 18, y + 22), fill=col, outline=(20, 20, 24, 255))
    save(sheet, 'capstone-sets-sheet.png', colors=255)


if __name__ == '__main__':
    main()
