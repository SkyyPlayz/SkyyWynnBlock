#!/usr/bin/env python3
"""SkyWynn Light Armor - concept sheets (cloud draft 2026-10-06).

Original pixel art, drawn from code (no copied art, no game files).
Run:  python3 research/cloud/light-armor/make_sheets.py
Writes the PNGs next to this script. Deterministic: same code -> same bytes.

How it draws: every figure is painted on a small 64 x 84 pixel grid, one
"part" (a set of grid pixels) at a time. Each part gets a 1-px dark outline
and a 4-step shade ramp lit from the top-left. The grid is then scaled up
with NEAREST so the pixels stay chunky.
"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__))
W, H = 64, 84          # figure grid
SCALE = 5              # set images: 320 x 420 figure
CHEST_SCALE = 8        # chest close-ups


def hx(s):
    s = s.lstrip('#')
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def ramp(*cols):
    """[outline, dark, mid, light, highlight]"""
    return [hx(c) for c in cols]


# ---------------------------------------------------------------- palettes
LEATHER = ramp('#0a090c', '#1c191f', '#2b2730', '#3f3946', '#58515f')
LEATHER_IN = ramp('#060507', '#121014', '#1a171d', '#242027', '#2e2a33')   # inner / far side
PANTS = ramp('#0a090b', '#18161a', '#232026', '#302c34', '#423d47')
STRAP = ramp('#1c1009', '#3e2516', '#5c3a22', '#7b5032', '#9a6a44')
BRASS = ramp('#3a2a0e', '#7a5a1e', '#b8892e', '#e2b95a', '#f6de96')
DUMMY = ramp('#4a453f', '#7e776c', '#968e81', '#ada596', '#c6bfb0')    # neutral mannequin
GOLD = ramp('#4a3208', '#9a6e18', '#d4a234', '#f0c860', '#fff0b0')

TIERS = [
    # name, level band, metal ramp
    ('Leather', 'Lv 1-13', BRASS),   # tier 1 = vanilla leather armor: NOT drawn, placeholder only
    ('Copper', 'Lv 10-18', ramp('#3b1a0c', '#8a4220', '#c26a34', '#e89558', '#ffc48e')),
    ('Iron', 'Lv 15-23', ramp('#24282e', '#5c646e', '#8e97a2', '#bcc4cc', '#eef2f5')),
    ('Thorium', 'Lv 20-28', ramp('#1c3324', '#3f6b4a', '#5e9468', '#8cc08e', '#cdebc6')),
    ('Cobalt', 'Lv 25-38', ramp('#121b3d', '#2a3f8a', '#3f63c4', '#6f95e6', '#b9d0ff')),
    ('Adamantite', 'Lv 35-43', ramp('#3a0c10', '#7a1a20', '#b42c30', '#e0574f', '#ffa192')),
    ('Mithril', 'Lv 40-49', ramp('#1e3a44', '#4e8c98', '#7ec4cc', '#b4ecee', '#f2ffff')),
    ('Onyxium', 'Lv 40-49', ramp('#160c22', '#3e2460', '#6b3fa0', '#a06cda', '#e4c8ff')),
]
GLOW = {'Onyxium': hx('#ff7af0'), 'Mithril': hx('#ffffff'), 'Adamantite': hx('#ffd0c8')}

BG = hx('#b4b9bf')
BG_SHADOW = hx('#9ca2a9')
INK = (34, 36, 40, 255)


# ---------------------------------------------------------------- mask helpers
def rect(x0, y0, x1, y1):
    return {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}


def _draw(fn):
    im = Image.new('1', (W, H), 0)
    fn(ImageDraw.Draw(im))
    px = im.load()
    return {(x, y) for x in range(W) for y in range(H) if px[x, y]}


def ell(x0, y0, x1, y1):
    return _draw(lambda d: d.ellipse((x0, y0, x1, y1), fill=1))


def poly(pts):
    return _draw(lambda d: d.polygon(pts, fill=1))


def mirror(m):
    return {(W - 1 - x, y) for x, y in m}


def both(m):
    return m | mirror(m)


def clip(m, y0=-99, y1=999, x0=-99, x1=999):
    return {(x, y) for x, y in m if y0 <= y <= y1 and x0 <= x <= x1}


def bottom_rim(m, w):
    """pixels of m within w rows of its lower edge"""
    return {(x, y) for x, y in m if any((x, y + k) not in m for k in range(1, w + 1))}


def top_rim(m, w):
    return {(x, y) for x, y in m if any((x, y - k) not in m for k in range(1, w + 1))}


# ---------------------------------------------------------------- painter
class Fig:
    def __init__(self):
        self.im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        self.px = self.im.load()
        self.metal = 0      # metal accent pixels (for the "leather dominates" check)
        self.kind = {}      # pixel -> 'leather' / 'metal' / ...

    def paint(self, mask, rp, pattern=None, outline=True, edge_ref=None, kind='leather'):
        """Shade a part: outline on its edge, light top-left, dark bottom-right."""
        mask = {p for p in mask if 0 <= p[0] < W and 0 <= p[1] < H}
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
            self.kind[(x, y)] = kind

    def dots(self, pts, rp, kind='metal'):
        """micro details: list of (x, y, ramp index)"""
        for x, y, i in pts:
            if 0 <= x < W and 0 <= y < H:
                self.px[x, y] = rp[i]
                self.kind[(x, y)] = kind

    def trim(self, rim, parent, rp):
        """metal trim inside a part: outline only where the part itself ends"""
        self.paint(rim, rp, edge_ref=parent, kind='metal')


# ---------------------------------------------------------------- patterns
def quilt(x, y, i):
    """diamond-quilted scales: dark seams on a 6-px diagonal lattice,
    each diamond lit on its upper-left side and shaded on its lower-right side"""
    if i == 0:
        return 0
    u, v = (x + y) % 6, (x - y) % 6
    if u == 0 or v == 0:
        return 1
    if u == 1:
        return 4 if v == 3 else 3
    if u == 5 or v == 1:
        return 1 if i <= 2 else 2
    return 2


def banded(*rows):
    def f(x, y, i):
        return 1 if i in (2, 3, 4) and y in rows else i
    return f


def tassel_pat(x0):
    def f(x, y, i):
        if i == 0:
            return 0
        if x == x0 + 3:
            return 1
        if x == x0 + 1:
            return 3
        return 2
    return f


# ---------------------------------------------------------------- tier config
def cfg_for(t):
    """accent coverage grows each tier; the shape language is the metal's own"""
    c = dict(rims=[], rim_w=2, collar=0, rivets=False, elbow=None, knee=None, gorget=False,
             shoulder=None, chest=None, medal=None, bracer=0, tassel=None, toe=False,
             beltplate=False, gold=False)
    if t == 1:   # Copper: thin plain trims
        c.update(rims=[1], collar=2, bracer=1, medal='ring', tassel='dot')
    if t == 2:   # Iron: layered banded plates + rivets
        c.update(rims=[1, 2], collar=2, rivets=True, elbow='full', bracer=2, tassel='rivet', medal='plate')
    if t == 3:   # Thorium: heavy collar, chunky shoulders, round boss
        c.update(rims=[1, 2], rim_w=3, collar=3, gorget=True, knee='cap', bracer=1,
                 tassel='cap', shoulder='thick', elbow='full', medal='boss')
    if t == 4:   # Cobalt: angular, pointed
        c.update(rims=[1, 2], collar=2, shoulder='peak', chest='vtrim', knee='point',
                 bracer=1, tassel='point', elbow='fin', medal='rhombus')
    if t == 5:   # Adamantite: spikes + crystal shards
        c.update(rims=[1, 2, 3], collar=2, shoulder='spikes', knee='spike',
                 bracer=1, tassel='point', elbow='spike', toe=True, medal='shard')
    if t == 6:   # Mithril: elegant, tall collar, curves
        c.update(rims=[1, 2, 3], rim_w=3, collar=3, shoulder='flare', chest='filigree', knee='cap',
                 bracer=2, tassel='cap', toe=True, beltplate=True, elbow='rim', medal='gem')
    if t == 7:   # Onyxium: ornate, crowned, glowing gem, gold filigree
        c.update(rims=[1, 2, 3], rim_w=3, collar=3, shoulder='crown', chest='filigree', knee='cap',
                 bracer=2, tassel='cap', toe=True, beltplate=True, elbow='rim', gold=True, medal='onyx')
    return c


LEAF = ["...44",
        "..432",
        ".3321",
        ".221.",
        "0...."]   # small leaf: tip up-right, stem down-left; digits = ramp index


def leaf(fig, x, y, rp, flip=False):
    pts = []
    for dy, row in enumerate(LEAF):
        for dx, ch in enumerate(row):
            if ch != '.':
                pts.append(((x + 4 - dx) if flip else (x + dx), y + dy, int(ch)))
    fig.dots(pts, rp)


def buckle(fig, x, y, rp, w=5, h=5):
    pts = []
    for dx in range(w):
        for dy in range(h):
            if dx in (0, w - 1) or dy in (0, h - 1):
                i = 3 if (dx == 0 or dy == 0) else 1
                if (dx, dy) == (0, 0):
                    i = 4
                if (dx, dy) in ((w - 1, 0), (0, h - 1)):
                    i = 2
                pts.append((x + dx, y + dy, i))
    pts += [(x + w // 2, y + 1, 3), (x + w // 2, y + 2, 2)]   # prong
    fig.dots(pts, rp)


def X(x, side):
    return x if side == 0 else W - 1 - x


# ---------------------------------------------------------------- the figure
def draw_figure(t, back=False, bust=False):
    name, band, M = TIERS[t]
    c = cfg_for(t)
    acc = M                                    # accents: buckles, leaves, studs
    G = GOLD if c['gold'] else M               # Onyxium uses gold for its filigree
    f = Fig()
    sides = (0, 1)

    def S(m, side):
        return m if side == 0 else mirror(m)

    # --- mannequin (neutral, faceless)
    if not bust:
        f.paint(rect(21, 48, 31, 81) | rect(32, 48, 42, 81), DUMMY, kind='dummy')
    for side in sides:
        f.paint(S(rect(13, 22, 19, 58), side), DUMMY, kind='dummy')
    f.paint(rect(27, 14, 36, 22), DUMMY, kind='dummy')
    if not bust:
        f.paint(rect(24, 0, 39, 17) | rect(23, 1, 40, 16) | rect(22, 3, 41, 14), DUMMY, kind='dummy')
        if back:
            f.dots([(x, 11, 1) for x in range(25, 39)], DUMMY, kind='dummy')

    # --- side tassels (behind the legs, darker = farther away)
    if not bust:
        for side in sides:
            for x0, y1 in ((15, 59), (17, 61)):
                f.paint(S(rect(x0, 47, x0 + 4, y1), side), LEATHER_IN)

    # --- legs: trousers, knee guards, boots
    if not bust:
        for side in sides:
            f.paint(S(rect(21, 48, 31, 72), side), PANTS)
            km = S(ell(21, 59, 31, 67), side)
            f.paint(km, LEATHER, pattern=banded(63) if c['knee'] is None else None)
            if c['knee'] and not back:
                kx = X(26, side)
                if c['knee'] == 'cap':
                    f.trim(top_rim(km, 2), km, M)
                    f.dots([(kx, 63, 4), (kx, 64, 1)], G)
                elif c['knee'] == 'point':
                    f.paint(S(poly([(22, 63), (26, 56), (30, 63)]), side), M, kind='metal')
                elif c['knee'] == 'spike':
                    f.paint(S(poly([(24, 61), (26, 53), (28, 61)]), side), M, kind='metal')
            bm = S(rect(21, 72, 31, 82) | rect(20, 77, 31, 82), side)
            f.paint(bm, LEATHER, pattern=banded(80))
            f.paint(S(rect(20, 70, 31, 74), side), LEATHER_IN if back else LEATHER)
            f.paint(S(rect(21, 76, 31, 78), side), STRAP)
            if not back:
                buckle(f, X(24, side) - (4 if side else 0), 75, acc, w=5, h=5)
            if c['toe'] and not back:
                f.trim(S(rect(20, 80, 31, 82), side), bm, M)

    # --- tassel skirt (long rectangular leather strips)
    if not bust:
        xs = [19, 23, 27, 31, 35, 39] if not back else [17, 21, 25, 29, 33, 37, 41]
        for k, x0 in enumerate(xs):
            y1 = 64 if k % 2 == 0 else 61
            if back:
                y1 = 63 if k % 2 == 0 else 65
            tm = rect(x0, 47, x0 + 4, y1)
            f.paint(tm, LEATHER, pattern=tassel_pat(x0))
            tip = c['tassel']
            if tip == 'dot':
                f.dots([(x0 + 2, y1 - 2, 3), (x0 + 2, y1 - 1, 1)], M)
            elif tip == 'rivet':
                f.dots([(x0 + 2, y1 - 3, 4), (x0 + 2, y1 - 2, 1)], M)
            elif tip == 'cap':
                f.trim(rect(x0, y1 - 1, x0 + 4, y1), tm, M)
                if c['gold']:
                    f.dots([(x0 + 2, y1 - 1, 3)], GOLD)
            elif tip == 'point':
                f.paint(poly([(x0, y1 - 1), (x0 + 4, y1 - 1), (x0 + 2, y1 + 3)]), M, kind='metal')

    # --- arms: layered upper arm, elbow cop, segmented bracer, finger-less hand guard
    for side in sides:
        f.paint(S(rect(13, 33, 19, 40), side), LEATHER, pattern=banded(36))
        em = S(ell(12, 39, 20, 46), side)
        if c['elbow'] == 'full':
            f.paint(em, M, kind='metal')
            f.dots([(X(16, side), 42, 4)], M)
        else:
            f.paint(em, LEATHER)
            if c['elbow'] in ('rim', 'fin', 'spike'):
                f.trim(top_rim(em, 2), em, M)
        if c['elbow'] == 'fin' and not back:
            f.paint(S(poly([(12, 41), (8, 44), (12, 45)]), side), M, kind='metal')
        if c['elbow'] == 'spike':
            f.paint(S(poly([(12, 41), (8, 43), (12, 45)]), side), M, kind='metal')
        br = S(poly([(13, 46), (19, 46), (20, 53), (12, 53)]), side)
        f.paint(br, LEATHER, pattern=banded(49, 51))
        if c['bracer'] >= 1:
            f.trim(top_rim(br, 2), br, G)
        if c['bracer'] >= 2:
            f.trim(bottom_rim(br, 2), br, M)
        if c['rivets']:
            f.dots([(X(14, side), 50, 4), (X(18, side), 50, 4)], M)
        f.paint(S(rect(13, 53, 19, 56), side), LEATHER)
        f.paint(S(rect(13, 56, 19, 58), side), DUMMY, kind='dummy')      # bare fingers
        f.dots([(X(x, side), 57, 1) for x in (15, 17)], DUMMY, kind='dummy')
        f.dots([(X(15, side), 54, 3), (X(16, side), 54, 2), (X(16, side), 55, 1)], acc)   # stud

    # --- chest piece (quilted front, smooth side panels)
    torso = rect(20, 21, 43, 48) | rect(21, 20, 42, 21)
    f.paint(torso, LEATHER, pattern=quilt)
    for side in sides:
        f.paint(S(rect(20, 23, 22, 48), side), LEATHER, edge_ref=torso, pattern=banded(30, 37))

    if not back:
        if c['gorget']:
            g = (ell(22, 14, 41, 31) - ell(23, 9, 40, 27)) & rect(22, 22, 41, 31)
            f.paint(g, M, kind='metal')
        if c['chest'] == 'vtrim':
            for side in sides:
                f.paint(S(poly([(22, 24), (25, 24), (32, 33), (31.5, 35)]), side), M, kind='metal')
        if c['chest'] == 'filigree':
            curve = [(23, 25), (24, 26), (25, 27), (25, 28), (24, 29), (24, 30), (24, 31), (25, 32), (26, 33),
                     (27, 34), (26, 35), (25, 36), (25, 37)]
            for side in sides:
                f.dots([(X(x, side), y, 3) for x, y in curve], G)
                f.dots([(X(x + 1, side), y, 1) for x, y in curve], G)
    elif t >= 6:
        f.trim(rect(31, 22, 32, 40), torso, G)    # spine line on the back

    # --- diagonal chest strap (wearer's right shoulder -> left hip) with the tier's chest piece
    sp = poly([(19, 25), (23, 21), (45, 40), (41, 43)])
    if back:
        sp = mirror(sp)
    f.paint(sp, STRAP, pattern=lambda x, y, i: 1 if i in (2, 3) and (x - y) % 4 == 0 else i)
    if not back:
        leaf(f, 23, 22, acc)
        m = c['medal']
        if m is None or m == 'ring':
            buckle(f, 29, 29, acc)
        elif m == 'plate':
            p = rect(28, 28, 35, 34)
            f.paint(p, M, kind='metal')
            f.dots([(29, 29, 4), (34, 29, 4), (29, 33, 4), (34, 33, 4)], M)
        elif m == 'boss':
            p = ell(27, 26, 36, 35)
            f.paint(p, M, kind='metal')
            f.dots([(31, 30, 4), (32, 30, 3), (31, 31, 3), (32, 31, 1)], M)
        elif m == 'rhombus':
            f.paint(poly([(31.5, 24), (37, 31), (31.5, 38), (26, 31)]), M, kind='metal')
            f.paint(poly([(31.5, 28), (34, 31), (31.5, 34), (29, 31)]), M, kind='metal')
        elif m == 'shard':
            f.paint(poly([(31.5, 22), (35.5, 29), (33.5, 38), (29.5, 38), (27.5, 29)]), M, kind='metal')
            f.paint(poly([(26, 31), (27.5, 27), (29, 32)]), M, kind='metal')
            f.paint(poly([(37, 31), (35.5, 27), (34, 32)]), M, kind='metal')
            f.dots([(30, 28, 4), (30, 29, 4), (31, 30, 3), (30, 30, 3)], M)
        elif m == 'gem':
            f.paint(poly([(31.5, 23), (36, 31), (31.5, 39), (27, 31)]), M, kind='metal')
            f.paint(ell(29, 28, 34, 34), M, kind='metal')
            f.dots([(30, 29, 4), (31, 29, 4), (30, 30, 4)], M)
            f.px[31, 30] = GLOW['Mithril']
        elif m == 'onyx':
            f.paint(poly([(31.5, 21), (34, 25), (31.5, 41), (29, 25)]), GOLD, kind='metal')
            f.paint(ell(26, 25, 37, 37), GOLD, kind='metal')
            f.paint(ell(28, 27, 35, 35), M, kind='metal')
            f.dots([(29, 29, 4), (30, 29, 4), (29, 30, 4), (30, 30, 3)], M)
            for p in ((32, 32), (33, 32), (32, 33)):
                f.px[p] = GLOW['Onyxium']

    # --- wide double waist belt with buckles, belt pouch on the left hip
    b1, b2 = rect(19, 40, 44, 44), rect(19, 44, 44, 48)
    f.paint(b1, STRAP, pattern=banded(42))
    f.paint(b2, STRAP, pattern=banded(46))
    if not back:
        if c['beltplate']:
            f.paint(rect(28, 40, 35, 44), G, kind='metal')
            f.dots([(29, 41, 4), (34, 43, 1)], G)
        else:
            buckle(f, 29, 40, acc)
        buckle(f, 34, 44, acc)
        leaf(f, 21, 40, acc)
        pouch = rect(37, 46, 44, 55)
        f.paint(pouch, STRAP)
        f.paint(rect(37, 46, 44, 50) | rect(39, 50, 42, 51), STRAP, pattern=lambda x, y, i: max(1, i - 1) if i else 0)
        f.dots([(40, 50, 3), (41, 50, 2), (40, 51, 1), (41, 51, 1)], acc)
    else:
        for x in (24, 39):
            f.dots([(x, 42, 3), (x, 46, 3)], acc)

    # --- raised stand-up collar
    tall = 2 if t >= 6 else 0
    f.paint(rect(24, 18 - tall, 39, 24), LEATHER_IN)
    for side in sides:
        flap = poly([(20, 16 - tall), (30, 18 - tall), (30, 25), (20, 25)]) if not back else \
            poly([(20, 16 - tall), (31, 18 - tall), (31, 25), (20, 25)])
        fm = S(flap, side)
        f.paint(fm, LEATHER, pattern=banded(21))
        if c['collar']:
            f.trim(top_rim(fm, c['collar']), fm, G)
        if t == 4:      # Cobalt: angular collar tip
            f.paint(S(poly([(19, 19), (20, 13), (23, 17)]), side), M, kind='metal')
        if t == 5:      # Adamantite: jagged collar points
            f.paint(S(poly([(20, 18), (21, 12), (23, 17)]), side), M, kind='metal')
            f.paint(S(poly([(24, 18), (25, 14), (27, 18)]), side), M, kind='metal')
        if not back:
            if t <= 1:
                leaf(f, X(21, side) - (4 if side else 0), 19, acc, flip=bool(side))
            else:
                f.dots([(X(28, side), 22, 3), (X(28, side), 23, 1)], acc)    # clasp studs

    # --- layered rounded shoulder caps (lowest plate first, top cap last)
    p3 = clip(ell(12, 24, 20, 36), y0=30)
    p2 = clip(ell(11, 19, 22, 33), y0=26)
    p1 = ell(10, 18, 23, 29)
    for side in sides:
        for k, pm in ((3, p3), (2, p2), (1, p1)):
            pm = S(pm, side)
            f.paint(pm, LEATHER, pattern=banded(23) if k == 1 else None)
            if k in c['rims']:
                if k == 1:
                    f.trim(bottom_rim(pm, c['rim_w']), pm, M)
                else:   # lower plates: a thin metal line inside the leather edge
                    f.paint(bottom_rim(pm, 2) - bottom_rim(pm, 1), M, outline=False, kind='metal')
        top = S(p1, side)
        if c['gold']:
            f.dots([(x, y, 3) for x, y in bottom_rim(top, 4) - bottom_rim(top, 3) if (x + y) % 2 == 0], GOLD)
        if c['rivets']:
            f.dots([(X(x, side), 27, 4) for x in (13, 16, 19)], M)
        if c['shoulder'] == 'thick':
            f.trim(top_rim(top, 2), top, M)
        elif c['shoulder'] == 'peak':
            f.trim(top_rim(top, 2), top, M)
            f.paint(S(poly([(12, 21), (15, 11), (19, 19)]), side), M, kind='metal')
        elif c['shoulder'] == 'spikes':
            for sx, h in ((12, 5), (16, 9), (20, 5)):
                f.paint(S(poly([(sx - 1.5, 20), (sx, 19 - h), (sx + 1.5, 20)]), side), M, kind='metal')
        elif c['shoulder'] == 'flare':
            f.trim(top_rim(top, 2), top, M)
        elif c['shoulder'] == 'crown':
            f.trim(top_rim(top, 2), top, M)
            for sx, h in ((12, 4), (16, 6), (20, 4)):
                f.paint(S(poly([(sx - 1.5, 19), (sx, 19 - h), (sx + 1.5, 19)]), side), GOLD, kind='metal')
        if not back:
            if t <= 1:
                leaf(f, X(14, side) - (4 if side else 0), 21, acc, flip=bool(side))
            elif t in (6, 7):
                f.dots([(X(16, side), 23, 4), (X(16, side), 24, 2)], M)
                f.px[X(16, side), 24] = GLOW['Mithril' if t == 6 else 'Onyxium']
    return f


# ---------------------------------------------------------------- output
def font(n):
    return ImageFont.load_default(size=n)


def armor_share(f):
    k = list(f.kind.values())
    metal = k.count('metal')
    armor = len(k) - k.count('dummy')
    return metal, armor


def scaled(f, s, bg=True):
    im = f.im.resize((W * s, H * s), Image.NEAREST)
    if not bg:
        return im
    base = Image.new('RGBA', im.size, BG)
    d = ImageDraw.Draw(base)
    d.ellipse((14 * s, 79 * s, 49 * s, 84 * s - 1), fill=BG_SHADOW)
    base.alpha_composite(im)
    return base


def label(im, text, sub, n=22):
    pad = 46
    out = Image.new('RGBA', (im.width, im.height + pad), BG)
    out.paste(im, (0, 0))
    d = ImageDraw.Draw(out)
    d.text((im.width // 2, im.height + 4), text, font=font(n), fill=INK, anchor='mt')
    d.text((im.width // 2, im.height + 27), sub, font=font(14), fill=(60, 64, 70, 255), anchor='mt')
    return out


def save(im, name):
    im = im.convert('RGB').quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(os.path.join(OUT, name), optimize=True)


def main():
    fronts, backs = [], []
    report = []
    for t, (name, band, M) in enumerate(TIERS):
        if t == 0:
            continue   # tier 1 = vanilla leather armor, no new design (Skyy 2026-10-06)
        fr = draw_figure(t)
        bk = draw_figure(t, back=True)
        bu = draw_figure(t, bust=True)
        metal, armor = armor_share(fr)
        report.append((name, metal, armor))
        # per-tier set: front + back
        a, b = scaled(fr, SCALE), scaled(bk, SCALE)
        pair = Image.new('RGBA', (a.width * 2 + 12, a.height), BG)
        pair.paste(a, (0, 0))
        pair.paste(b, (a.width + 12, 0))
        d = ImageDraw.Draw(pair)
        d.text((8, 6), 'front', font=font(14), fill=INK)
        d.text((a.width + 20, 6), 'back', font=font(14), fill=INK)
        save(label(pair, f'{name} Light Armor', f'{band}  |  concept, cloud draft'), f'{name.lower()}-set.png')
        # chest close-up (bust, no head)
        crop = bu.im.crop((4, 9, 60, 62))
        ch = crop.resize((crop.width * CHEST_SCALE, crop.height * CHEST_SCALE), Image.NEAREST)
        base = Image.new('RGBA', ch.size, BG)
        base.alpha_composite(ch)
        save(label(base, f'{name} Light Chest', f'{band}  |  front close-up'), f'{name.lower()}-chest.png')
        fronts.append(a)
        backs.append(b)

    # combined sheet: fronts on top, backs below
    fw, fh = fronts[0].size
    gap, top, labh = 16, 70, 50
    fronts.insert(0, None)
    backs.insert(0, None)
    sheet_w = len(TIERS) * fw + (len(TIERS) + 1) * gap
    sheet_h = top + 2 * (fh + labh) + gap * 3
    sheet = Image.new('RGBA', (sheet_w, sheet_h), BG)
    d = ImageDraw.Draw(sheet)
    d.text((sheet_w // 2, 18), 'SkyWynn Light Armor - concept (cloud draft)', font=font(34), fill=INK, anchor='mt')
    for i, (name, band, M) in enumerate(TIERS):
        x = gap + i * (fw + gap)
        y = top
        if fronts[i] is None:   # greyed placeholder: tier 1 stays vanilla
            y2 = top + fh + labh + gap
            d.rectangle((x, y, x + fw - 1, y2 + fh - 1), fill=(166, 171, 177, 255), outline=(140, 145, 151, 255), width=3)
            for k, line in enumerate(['Tier 1', 'vanilla leather', 'armor', '', '(no new design)']):
                d.text((x + fw // 2, y + 140 + k * 30), line, font=font(22 if k < 3 else 18),
                       fill=(110, 114, 120, 255), anchor='mt')
            d.text((x + fw // 2, y + fh + 6), 'Leather', font=font(24), fill=(110, 114, 120, 255), anchor='mt')
            d.text((x + fw // 2, y + fh + 32), band + '  (vanilla)', font=font(14), fill=(110, 114, 120, 255), anchor='mt')
            continue
        sheet.paste(fronts[i], (x, y))
        d.text((x + fw // 2, y + fh + 6), name, font=font(24), fill=INK, anchor='mt')
        d.text((x + fw // 2, y + fh + 32), band + '  (front)', font=font(14), fill=(60, 64, 70, 255), anchor='mt')
        sw = [M[3], M[2], M[1]]
        for j, col in enumerate(sw):
            d.rectangle((x + 6 + j * 16, y + 6, x + 18 + j * 16, y + 18), fill=col, outline=M[0])
        y2 = top + fh + labh + gap
        sheet.paste(backs[i], (x, y2))
        d.text((x + fw // 2, y2 + fh + 6), name + ' (back)', font=font(16), fill=(60, 64, 70, 255), anchor='mt')
    save(sheet, 'light-armor-sheet.png')

    for name, metal, armor in report:
        print(f'{name:11s} metal accents {metal:4d} px of {armor:4d} armor px = {100 * metal / armor:4.1f}%')


if __name__ == '__main__':
    main()
