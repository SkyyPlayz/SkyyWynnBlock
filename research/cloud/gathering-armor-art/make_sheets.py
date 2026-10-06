#!/usr/bin/env python3
"""SkyWynn Mining + Farming armor - concept sheets (cloud draft 2026-10-06).

Original pixel art, drawn from code (no copied art, no game files).
Run:  python3 research/cloud/gathering-armor-art/make_sheets.py
Writes mining-sheet.png and farming-sheet.png next to this script
(--v1 also rewrites farming-sheet-v1.png, the replaced metal-farmer sheet).
Deterministic: same code -> same bytes.

Same style as research/cloud/light-armor/make_sheets.py (helpers copied, not
imported): figures on a 64 x 84 grid (+ 8 rows on top for hats / crests),
1-px dark outline, 4-step ramp lit from the top-left, NEAREST upscale.

Looks: research/cloud/Gathering-Armor-Mining-Farming.md sections 1.1, 2.1 and 6.
Mining = dark miner's leather + small metal plates + a lamp helmet that
brightens each tier. Farming v2 (Skyy LOCKED 2026-10-06) = CROP armor: the
v1 farmer look (straw hat, rolled sleeves, apron, coat) made from the crop of
each Farming Bench step, Wheat first (CROPS / draw_crop_farmer). Farming v1 =
straw hat + linen clothes with metal trims (FARMING / draw_farmer, --v1). Each tier keeps the previous tier's
pieces and adds its own (the set is an upgrade of the lower piece).
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__))
W, H = 64, 84
TOP = 8
SCALE = 5


def hx(s):
    s = s.lstrip('#')
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def ramp(*cols):
    """[outline, dark, mid, light, highlight]"""
    return [hx(c) for c in cols]


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3)) + (255,)


# ---------------------------------------------------------------- palettes
DUMMY = ramp('#4a453f', '#7e776c', '#968e81', '#ada596', '#c6bfb0')
GOLD = ramp('#4a3208', '#9a6e18', '#d4a234', '#f0c860', '#fff0b0')
# metal ramps = the same guesses as research/cloud/light-armor (UNVERIFIED vs vanilla)
METALS = {
    'Copper': ramp('#3b1a0c', '#8a4220', '#c26a34', '#e89558', '#ffc48e'),
    'Iron': ramp('#24282e', '#5c646e', '#8e97a2', '#bcc4cc', '#eef2f5'),
    'Thorium': ramp('#1c3324', '#3f6b4a', '#5e9468', '#8cc08e', '#cdebc6'),
    'Cobalt': ramp('#121b3d', '#2a3f8a', '#3f63c4', '#6f95e6', '#b9d0ff'),
    'Adamantite': ramp('#3a0c10', '#7a1a20', '#b42c30', '#e0574f', '#ffa192'),
    'Mithril': ramp('#1e3a44', '#4e8c98', '#7ec4cc', '#b4ecee', '#f2ffff'),
    'Onyxium': ramp('#160c22', '#3e2460', '#6b3fa0', '#a06cda', '#e4c8ff'),
}
NONE = ramp('#2a2a2c', '#56565a', '#707074', '#8c8c90', '#a8a8ac')   # T0: stone grey (no metal)

# mining
LEATHER = ramp('#0a090c', '#1c191f', '#2b2730', '#3f3946', '#58515f')
LEATHER_IN = ramp('#060507', '#121014', '#1a171d', '#242027', '#2e2a33')
BROWN = ramp('#1c1009', '#3e2516', '#5c3a22', '#7b5032', '#9a6a44')
SHIRT_M = ramp('#1a1c20', '#383c44', '#4a4f58', '#5c626c', '#737a84')    # grey work shirt
SAND = ramp('#4a3a20', '#9a8458', '#b8a070', '#d2bc8c', '#ecdcb0')       # sandstone wraps (Thorium+)
SHALE = ramp('#1a1e22', '#3a4148', '#4b545c', '#5e6870', '#76828a')      # shale cloak (Cobalt+)
# farming
STRAW = ramp('#4a3a10', '#a8862e', '#c8a444', '#e2c262', '#f6e08e')
FIBRE = ramp('#36321e', '#7e7650', '#9a9266', '#b4ac80', '#cec79c')      # T0 rough fibre shirt
LINEN = ramp('#4a4436', '#a69c84', '#c4bba2', '#ddd5bf', '#f2ecdc')
COTTON = ramp('#4c4c4c', '#b4b4ae', '#d0d0ca', '#e6e6e0', '#fafaf6')
BLUE_COT = ramp('#14203a', '#2e4a7c', '#3e60a0', '#5a80c0', '#86a8dc')
SILK = ramp('#4a4458', '#b0a8c4', '#cac4da', '#e0dcec', '#f6f4fc')
BLACK = ramp('#08080a', '#18171c', '#24222a', '#333038', '#48444e')
CANVAS = ramp('#2e2010', '#6a4e2c', '#86663c', '#a2804e', '#bc9a66')     # apron
TROUSER = ramp('#1e140c', '#4a3422', '#5e442e', '#74563a', '#8a6a48')
TROUSER_B = ramp('#0e1424', '#22304e', '#2e3e62', '#3c4e78', '#4e6290')
COAT = ramp('#14200e', '#2c4220', '#3a5428', '#4a6a32', '#5e8240')      # waxed green coat
LINING = ramp('#3a0c14', '#7a1a2a', '#9c2638', '#c03c4c', '#e06a74')    # silk lining
ROPE = ramp('#3a2a14', '#7a6034', '#a68650', '#c8a868', '#e2c88a')
SCARF = ramp('#3a0e0a', '#8a2a1c', '#b03a26', '#d05a3a', '#ec8a5c')
FLOWERS = [hx('#ffffff'), hx('#ffd84a'), hx('#ff8ab4'), hx('#a8d8ff')]

BG = hx('#b4b9bf')
BG_SHADOW = hx('#9ca2a9')
INK = (34, 36, 40, 255)

MINING = [  # T, name, band, metal key, lamp glow (colour, strength 0..1)
    (0, "Miner's Leather", 'Lv 1-13', None, None),
    (1, 'Copper Miner', 'Lv 5-18', 'Copper', ('#ffd27a', 0.45)),
    (2, 'Iron Miner', 'Lv 15-23', 'Iron', ('#ffe49a', 0.55)),
    (3, 'Thorium Miner', 'Lv 20-28', 'Thorium', ('#fff2b4', 0.75)),
    (4, 'Cobalt Miner', 'Lv 25-38', 'Cobalt', ('#d8ecff', 0.80)),
    (5, 'Adamantite Miner', 'Lv 35-43', 'Adamantite', ('#fff6dc', 0.90)),
    (6, 'Mithril Miner', 'Lv 40-49', 'Mithril', ('#e6ffff', 1.0)),
    (7, 'Onyxium Miner', 'Lv 40-49 (50+ later)', 'Onyxium', ('#ff8af2', 1.0)),
]
FARMING = [
    (0, 'Straw Farmer', 'Lv 1-13', None),
    (1, 'Copper Farmer', 'Lv 5-18', 'Copper'),
    (2, 'Iron Farmer', 'Lv 15-23', 'Iron'),
    (3, 'Thorium Farmer', 'Lv 20-28', 'Thorium'),
    (4, 'Cobalt Farmer', 'Lv 25-38', 'Cobalt'),
    (5, 'Adamantite Farmer', 'Lv 35-43', 'Adamantite'),
    (6, 'Mithril Farmer', 'Lv 40-49', 'Mithril'),
    (7, 'Onyxium Farmer', 'Lv 40-49 (50+ later)', 'Onyxium'),
]


# ---------------------------------------------------------------- mask helpers (copied from light-armor, + TOP rows)
def rect(x0, y0, x1, y1):
    return {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}


def _draw(fn):
    im = Image.new('1', (W, H + TOP), 0)
    fn(ImageDraw.Draw(im))
    px = im.load()
    return {(x, y - TOP) for x in range(W) for y in range(H + TOP) if px[x, y]}


def ell(x0, y0, x1, y1):
    return _draw(lambda d: d.ellipse((x0, y0 + TOP, x1, y1 + TOP), fill=1))


def poly(pts):
    return _draw(lambda d: d.polygon([(x, y + TOP) for x, y in pts], fill=1))


def line(pts, w=1):
    return _draw(lambda d: d.line([(x, y + TOP) for x, y in pts], fill=1, width=w))


def mirror(m):
    return {(W - 1 - x, y) for x, y in m}


def clip(m, y0=-99, y1=999, x0=-99, x1=999):
    return {(x, y) for x, y in m if y0 <= y <= y1 and x0 <= x <= x1}


def bottom_rim(m, w):
    return {(x, y) for x, y in m if any((x, y + k) not in m for k in range(1, w + 1))}


def top_rim(m, w):
    return {(x, y) for x, y in m if any((x, y - k) not in m for k in range(1, w + 1))}


def X(x, side):
    return x if side == 0 else W - 1 - x


def S(m, side):
    return m if side == 0 else mirror(m)


# ---------------------------------------------------------------- painter
class Fig:
    def __init__(self):
        self.im = Image.new('RGBA', (W, H + TOP), (0, 0, 0, 0))
        self._px = self.im.load()
        self.kind = {}

    def get(self, x, y):
        return self._px[x, y + TOP]

    def set(self, x, y, col, kind='trim'):
        if 0 <= x < W and -TOP <= y < H:
            self._px[x, y + TOP] = col
            self.kind[(x, y)] = kind

    def paint(self, mask, rp, pattern=None, outline=True, edge_ref=None, kind='cloth'):
        mask = {p for p in mask if 0 <= p[0] < W and -TOP <= p[1] < H}
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
            self.set(x, y, rp[i], kind)

    def dots(self, pts, rp, kind='trim'):
        for x, y, i in pts:
            self.set(x, y, rp[i], kind)

    def trim(self, rim, parent, rp):
        self.paint(rim, rp, edge_ref=parent, kind='trim')


# ---------------------------------------------------------------- patterns
def banded(*rows):
    def f(x, y, i):
        return 1 if i in (2, 3, 4) and y in rows else i
    return f


def weave(x, y, i):
    """straw / rough cloth weave"""
    if i == 0:
        return 0
    if (x // 2 + y // 2) % 2 == 0:
        return max(1, i - 1) if (x + y) % 2 == 0 else i
    return min(4, i + 1) if (x + y) % 3 == 0 and i >= 2 else i


def fine(x, y, i):
    """light linen texture"""
    if i in (2, 3) and (x * 3 + y) % 7 == 0:
        return i - 1
    return i


def wrap_pat(x, y, i):
    if i == 0:
        return 0
    return 1 if (x + y) % 3 == 0 else (3 if (x + y) % 3 == 1 and i >= 2 else i)


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
    pts += [(x + w // 2, y + 1, 3), (x + w // 2, y + 2, 2)]
    fig.dots(pts, rp)


def rivet(fig, x, y, rp):
    fig.dots([(x, y, 4), (x + 1, y, 2), (x, y + 1, 2), (x + 1, y + 1, 1)], rp)


def mannequin(f, back):
    f.paint(rect(21, 48, 31, 81) | rect(32, 48, 42, 81), DUMMY, kind='dummy')
    for side in (0, 1):
        f.paint(S(rect(13, 22, 19, 58), side), DUMMY, kind='dummy')
    f.paint(rect(27, 14, 36, 22), DUMMY, kind='dummy')
    f.paint(rect(24, 0, 39, 17) | rect(23, 1, 40, 16) | rect(22, 3, 41, 14), DUMMY, kind='dummy')
    if back:
        f.dots([(x, 11, 1) for x in range(25, 39)], DUMMY, kind='dummy')


def hands(f, side, rp):
    f.paint(S(rect(13, 53, 19, 58), side), rp)
    f.dots([(X(x, side), 58, 1) for x in (15, 17)], rp)


# ================================================================ MINING
def draw_miner(t, back=False):
    T, name, band, mk, lamp = MINING[t]
    M = METALS[mk] if mk else NONE
    f = Fig()
    mannequin(f, back)
    sides = (0, 1)

    # --- shale cloak behind everything (Cobalt+): visible at the sides in front, covers the back
    if t >= 4:
        cl = poly([(18, 19), (45, 19), (48, 66), (15, 66)])
        f.paint(cl, SHALE if t != 7 else LEATHER_IN,
                pattern=lambda x, y, i: (1 if i >= 2 and (x - 16 + (y > 45)) % 5 == 0 else (3 if i == 2 and (x - 16) % 5 == 1 else i)))
        if t >= 6:
            f.trim(bottom_rim(cl, 2), cl, M)

    # --- legs: leather trousers, knee pads, heavy boots with toe caps
    for side in sides:
        f.paint(S(rect(21, 48, 31, 73), side), LEATHER, pattern=banded(55))
        if t >= 3:
            f.paint(S(rect(21, 67, 31, 72), side), SAND, pattern=wrap_pat)      # sandstone wraps
        km = S(ell(21, 58, 31, 66), side)
        f.paint(km, M if t >= 1 else BROWN, kind='trim' if t else 'cloth')
        if t >= 2:
            rivet(f, X(23, side) - (1 if side else 0), 61, M)
            rivet(f, X(28, side) - (1 if side else 0), 61, M)
        if t >= 5 and not back:
            f.paint(S(poly([(23, 60), (26, 54), (29, 60)]), side), M, kind='trim')
        bm = S(rect(21, 73, 31, 82) | rect(20, 77, 31, 82), side)
        f.paint(bm, BROWN, pattern=banded(79))
        f.paint(S(rect(20, 73, 31, 75), side), LEATHER)
        if t >= 1 and not back:
            f.trim(S(rect(20, 80, 31, 82), side), bm, M)                    # steel toe cap
        if t >= 1:
            f.dots([(X(x, side), 74, 3) for x in (22, 25, 28)], M)

    # --- arms: grey shirt sleeves, leather gloves to the elbow, metal bracers
    for side in sides:
        f.paint(S(rect(13, 30, 19, 44), side), SHIRT_M, pattern=banded(37))
        gl = S(poly([(13, 44), (19, 44), (20, 54), (12, 54)]), side)
        f.paint(gl, LEATHER, pattern=banded(48))
        if t >= 3:
            f.paint(S(rect(12, 49, 20, 52), side), SAND, pattern=wrap_pat)
        if t >= 1:
            f.trim(top_rim(gl, 2), gl, M)
        if t >= 5:
            f.trim(S(rect(12, 50, 20, 53), side) & gl, gl, M)
        hands(f, side, LEATHER)

    # --- shirt + leather vest with ore pouches, stone-grey strap, tool belt
    torso = rect(20, 21, 43, 48) | rect(21, 20, 42, 21)
    f.paint(torso, SHIRT_M, pattern=fine)
    if not back:
        for side in sides:
            vest = S(poly([(20, 21), (28, 21), (30, 30), (29, 48), (20, 48)]), side)
            f.paint(vest, LEATHER, pattern=banded(33))
            pouch = S(rect(22, 30, 27, 36), side)
            f.paint(pouch, BROWN)
            f.paint(S(rect(22, 30, 27, 32), side), BROWN, pattern=lambda x, y, i: max(1, i - 1) if i else 0)
            f.dots([(X(24, side), 32, 3 if t else 2), (X(25, side), 32, 2 if t else 1)], M)
            if t >= 1:      # copper rivets down the vest edge
                for y in (24, 39, 44):
                    rivet(f, X(27, side) - (1 if side else 0), y, M)
            if t >= 5:      # heavy plate over the vest
                pl = S(poly([(21, 37), (28, 37), (29, 46), (21, 46)]), side)
                f.paint(pl, M, kind='trim')
                rivet(f, X(22, side) - (1 if side else 0), 39, M)
        f.dots([(31, y, 1) for y in range(22, 41)] + [(32, y, 2) for y in range(22, 41)], SHIRT_M, kind='cloth')
        if t >= 6:          # glowing ore gem on the chest centre
            f.paint(poly([(31.5, 25), (34, 28), (31.5, 31), (29, 28)]), M, kind='trim')
            f.set(31, 27, mix(M[4], hx(lamp[0]), 0.6))
        if t == 7:
            f.paint(rect(30, 32, 33, 40), GOLD, kind='trim')
    else:
        if t < 4:
            vb = rect(20, 21, 43, 48)
            f.paint(vb, LEATHER, pattern=banded(33))
            f.paint(rect(28, 25, 35, 30), BROWN)                 # lamp battery pack on the back strap
            f.dots([(29, 26, 4), (30, 26, 3)], BROWN)
    # stone-grey strap crossing the chest
    sp = poly([(19, 25), (23, 21), (45, 40), (41, 43)])
    if back:
        sp = mirror(sp)
    if not (back and t >= 4):
        f.paint(sp, NONE if t == 0 else ramp('#262628', '#4e4e52', '#66666a', '#7e7e82', '#98989c'),
                pattern=lambda x, y, i: 1 if i in (2, 3) and (x - y) % 4 == 0 else i)
        if t >= 1 and not back:
            buckle(f, 34, 31, M, w=4, h=4)

    # belt: wide leather tool belt, buckle, hammer loop + ore pouch
    belt = rect(19, 42, 44, 47)
    f.paint(belt, BROWN, pattern=banded(44))
    if not back:
        buckle(f, 29, 42, M if t else NONE, w=6, h=6)
        pouch = rect(37, 46, 44, 55)
        f.paint(pouch, BROWN)
        f.paint(rect(37, 46, 44, 49), BROWN, pattern=lambda x, y, i: max(1, i - 1) if i else 0)
        f.dots([(40, 49, 3), (41, 49, 2)], M)
        # little pick hanging on the left hip
        f.paint(line([(22, 46), (22, 57)], 1), BROWN)
        f.paint(poly([(18, 47), (22, 45), (26, 47), (22, 48)]), M if t else NONE, kind='trim')
    else:
        for x in (22, 41):
            f.dots([(x, 44, 3), (x, 45, 1)], M)
        if t >= 4:
            f.paint(rect(28, 22, 35, 24), M, kind='trim')        # cloak clasp bar

    # --- shoulder plates (Iron+); cloak clasp in front (Cobalt+)
    for side in sides:
        if t >= 2:
            sh = S(ell(11, 19, 23, 31), side)
            f.paint(sh, M, pattern=banded(25), kind='trim')
            if t >= 3:
                f.paint(S(clip(ell(11, 24, 21, 35), y0=31), side), M, kind='trim')
            rivet(f, X(14, side) - (1 if side else 0), 22, M)
            rivet(f, X(19, side) - (1 if side else 0), 22, M)
            if t == 7:
                f.paint(S(clip(ell(11, 19, 23, 31), y0=28) - clip(ell(11, 19, 23, 31), y0=30), side), GOLD, outline=False)
        else:
            sh = S(ell(12, 20, 22, 31), side)
            f.paint(sh, LEATHER, pattern=banded(25))
        if t >= 4 and not back:
            f.dots([(X(25, side), 21, 3), (X(25, side), 22, 1)], M)

    # --- collar
    f.paint(rect(24, 17, 39, 22), SHIRT_M if t < 4 else SHALE, pattern=banded(19))

    # --- HELMET: leather cap (T0) -> metal hard hat with a lamp that brightens each tier
    if t == 0:
        cap = ell(21, -4, 42, 14) & rect(21, -4, 42, 6)
        f.paint(cap, LEATHER, pattern=banded(2))
        f.paint(rect(20, 5, 43, 7), LEATHER)
        f.paint(rect(21, 2, 42, 3), NONE)                         # stone-grey band, no metal, no lamp
    else:
        dome = ell(20 if t != 2 else 22, -6 if t >= 3 else -4, 43 if t != 2 else 41, 14) & rect(19, -8, 44, 6)
        f.paint(dome, M, kind='trim', pattern=banded(0) if t in (2, 5) else None)
        brim = rect(18, 5, 45, 7) if t not in (2, 4) else rect(20, 5, 43, 7)
        f.paint(brim, M, kind='trim')
        if t == 2:
            for x in (24, 39):
                rivet(f, x, 1, M)
        if t == 5:      # heavy: ridge plates
            f.paint(rect(30, -7, 33, 5), M, kind='trim')
        if t == 6:      # pale mithril crest
            crest = poly([(29, -2), (31.5, -9), (34, -2)]) | rect(30, -6, 33, 4)
            f.paint(crest, M, kind='trim')
            f.dots([(31, -6, 4), (31, -5, 4)], M)
        if t == 7:      # onyx crown points + gold band
            f.paint(rect(19, 3, 44, 4), GOLD, outline=False, kind='trim')
            for sx in (23, 40):
                f.paint(poly([(sx - 2, -1), (sx, -8), (sx + 2, -1)]), GOLD, kind='trim')
        if not back:
            # lamp housing + lens; glow halo grows with the tier
            col, st = hx(lamp[0]), lamp[1]
            lx, ly = 31, -2 if t >= 3 else 0
            house = ell(lx - 3, ly - 3, lx + 4, ly + 4)
            f.paint(house, BROWN if t < 3 else M, kind='trim')
            lens = ell(lx - 2, ly - 2, lx + 3, ly + 3)
            for (x, y) in lens:
                f.set(x, y, mix(hx('#5a5040'), col, 0.4 + 0.6 * st), 'glow')
            f.set(lx - 1, ly - 1, hx('#ffffff'), 'glow')
            rr = 3 + int(st * 4)
            for y in range(ly - rr - 2, ly + rr + 3):
                for x in range(lx - rr - 2, lx + rr + 3):
                    d2 = (x - lx - 0.5) ** 2 + (y - ly - 0.5) ** 2
                    if 3.5 ** 2 < d2 <= (rr + 2) ** 2 and -TOP <= y < H:
                        a = st * 0.55 * (1 - (d2 ** 0.5 - 3.5) / (rr - 1.5))
                        if a <= 0:
                            continue
                        if (x, y) in f.kind:
                            f._px[x, y + TOP] = mix(f.get(x, y), col, a)
                        else:   # soft glow over the empty background (alpha)
                            f._px[x, y + TOP] = col[:3] + (int(255 * a * 0.8),)
            if st >= 0.9:   # sparkle rays on the brightest lamps
                for k in range(3, 6):
                    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                        x, y = lx + (dx * k if dx < 0 else dx * k + 1), ly + (dy * k if dy < 0 else dy * k + 1)
                        if (x, y) not in f.kind and -TOP <= y < H:
                            f._px[x, y + TOP] = col[:3] + (int(255 * (1.2 - k * 0.18)),)
            if t == 4:      # Cobalt: lens visor (goggles) over the face
                f.paint(rect(24, 9, 39, 12), LEATHER)
                for gx in (25, 33):
                    g = ell(gx, 8, gx + 5, 13)
                    f.paint(g, M, kind='trim')
                    f.paint(ell(gx + 1, 9, gx + 4, 12), [mix(c_, hx('#9ad0ff'), 0.6) for c_ in M], outline=False)
                    f.set(gx + 1, 9, hx('#ffffff'))
        else:
            f.paint(rect(22, 8, 41, 9), BROWN)                    # chin-strap / lamp cable at the back
    return f


# ================================================================ FARMING
def draw_farmer(t, back=False):
    T, name, band, mk = FARMING[t]
    M = METALS[mk] if mk else ROPE
    f = Fig()
    mannequin(f, back)
    sides = (0, 1)

    shirt = {0: FIBRE, 1: LINEN, 2: LINEN, 3: COTTON, 4: BLUE_COT, 5: COTTON, 6: SILK, 7: COTTON}[t]
    trous = TROUSER_B if t == 4 else (BLACK if t == 7 else TROUSER)

    # --- long coat behind (Adamantite+)
    coat = {5: COAT, 6: SILK, 7: BLACK}.get(t)
    if coat:
        cb = poly([(19, 21), (44, 21), (46, 68), (17, 68)])
        f.paint(cb, coat, pattern=banded(45) if back else None)
        if not back:
            f.paint(poly([(19, 40), (24, 40), (24, 68), (17, 68)]), coat)
            f.paint(poly([(39, 40), (44, 40), (46, 68), (39, 68)]), coat)
            f.paint(rect(24, 48, 25, 67) | rect(38, 48, 39, 67), LINING if t != 7 else GOLD, outline=False)
        f.trim(bottom_rim(cb, 2), cb, M if t != 7 else GOLD)

    # --- legs: trousers, boots (iron-bound from Iron)
    for side in sides:
        f.paint(S(rect(21, 48, 31, 74), side), trous, pattern=fine)
        f.dots([(X(26, side), y, 1) for y in range(52, 72, 2)], trous, kind='cloth')    # seam
        if t >= 1 and not coat:
            f.paint(S(rect(23, 62, 28, 66), side), trous, pattern=lambda x, y, i: max(1, i - 1) if i else 0)  # knee patch
        bm = S(rect(21, 74, 31, 82) | rect(20, 77, 31, 82), side)
        f.paint(bm, BROWN if t != 7 else BLACK, pattern=banded(80))
        f.paint(S(rect(20, 73, 31, 75), side), BROWN if t != 7 else BLACK)
        if t >= 2:
            f.trim(S(rect(21, 76, 31, 77), side), bm, M)
            f.trim(S(rect(20, 80, 31, 82), side), bm, M)
        if t >= 1:
            f.dots([(X(25, side), 74, 3), (X(25, side), 75, 1)], M)

    if coat and back:   # the coat skirt hangs over the legs at the back
        cs = clip(cb, y0=44)
        f.paint(cs, coat, edge_ref=cb, pattern=lambda x, y, i: 1 if i >= 2 and x in (31, 32) and y > 49 else i)
        f.trim(bottom_rim(cb, 2), cb, M if t != 7 else GOLD)

    # --- arms: sleeves rolled to the elbow, bare forearm, work gloves (Iron+)
    for side in sides:
        sl = S(rect(13, 22, 19, 41), side)
        f.paint(sl, coat if coat else shirt, pattern=fine)
        f.paint(S(rect(12, 40, 20, 43), side), coat if coat else shirt, pattern=banded(42))   # rolled cuff
        if t >= 4:
            f.trim(S(rect(12, 42, 20, 43), side), S(rect(12, 40, 20, 43), side), M if t != 7 else GOLD)
        if t >= 2:
            gl = S(poly([(13, 49), (19, 49), (20, 55), (12, 55)]), side)
            f.paint(gl, CANVAS if t < 7 else BLACK, pattern=banded(51))
            hands(f, side, CANVAS if t < 7 else BLACK)
            if t >= 3:
                f.dots([(X(16, side), 50, 3), (X(16, side), 51, 1)], M)

    # --- shirt
    torso = rect(20, 21, 43, 48) | rect(21, 20, 42, 21)
    f.paint(torso, shirt if not (coat and back) else coat, pattern=weave if t == 0 else fine)
    if coat and back:   # coat back: centre vent + lining peek + a tier trim at the collar
        f.dots([(31, y, 0) for y in range(40, 49)] + [(32, y, 3) for y in range(40, 49)], coat, kind='cloth')
        f.trim(rect(22, 21, 41, 22), torso, M if t != 7 else GOLD)
    if not back:
        f.paint(poly([(28, 20), (35, 20), (31.5, 27)]), shirt, pattern=lambda x, y, i: max(1, i - 1) if i else 0)
        for y in (29, 33, 37):
            f.dots([(31, y, 1), (32, y, 3)], M if t >= 3 else shirt)          # buttons / clasps
        if t == 6:      # mithril thread embroidery
            for x, y in ((24, 25), (25, 26), (26, 25), (37, 25), (38, 26), (39, 25), (24, 30), (39, 30)):
                f.dots([(x, y, 4)], M)
    # coat fronts (Adamantite+)
    if coat and not back:
        for side in sides:
            lap = S(poly([(20, 21), (26, 21), (28, 34), (26, 48), (20, 48)]), side)
            f.paint(lap, coat)
            f.paint(S(line([(26, 21), (28, 34), (26, 48)], 1), side), LINING if t != 7 else GOLD, outline=False)
            f.dots([(X(25, side), 36, 3), (X(25, side), 37, 1)], M if t != 7 else GOLD)
        if t == 5:
            for y in (30, 38):
                f.dots([(23, y, 3), (24, y, 2), (39, y, 3), (40, y, 2)], M)    # fasteners
    # back: apron ties crossing
    if back and t >= 1 and not coat:
        for a in (line([(21, 22), (42, 42)], 2), line([(42, 22), (21, 42)], 2)):
            f.paint(a, CANVAS if t < 7 else BLACK, outline=False, pattern=banded())
        f.dots([(31, 45, 3), (32, 45, 3), (30, 46, 1), (33, 46, 1)], CANVAS)

    # --- apron (Copper+): bib on the chest, skirt to the knee, a pocket
    if t >= 1 and not back:
        ap = rect(25, 26, 38, 40) | rect(23, 40, 40, 64)
        ac = CANVAS if t < 7 else BLACK
        f.paint(ap, ac, pattern=fine)
        f.paint(rect(27, 50, 36, 56), ac, pattern=lambda x, y, i: max(1, i - 1) if i else 0)    # pocket
        f.dots([(x, 50, 3) for x in range(28, 36)], ac)
        for side in sides:
            f.paint(S(line([(25, 26), (23, 20)], 2), side), ac, outline=False, pattern=banded())  # neck straps
            f.dots([(X(25, side), 27, 3), (X(25, side), 28, 1)], M)                         # strap rivets
        if t >= 4:
            f.trim(bottom_rim(ap, 1) | {(x, y) for x, y in ap if x in (23, 40) and y >= 40}, ap, M if t != 7 else GOLD)
        if t == 7:      # gold wheat-ear emblem on the bib
            for k, (x, y) in enumerate(((31, 36), (31, 35), (31, 34), (31, 33), (31, 32), (31, 31))):
                f.dots([(x, y, 2)], GOLD)
                if k >= 2:
                    f.dots([(x - 1, y - 1, 3), (x + 1, y - 1, 3)], GOLD)
            f.dots([(31, 30, 4)], GOLD)
        if t == 3:      # a seed packet / tool in the pocket
            f.paint(rect(29, 47, 31, 51), M, kind='trim')

    # --- belt: rope (T0) -> leather with a tier buckle
    belt = rect(19, 42, 44, 45)
    if t == 0:
        f.paint(belt, ROPE, pattern=wrap_pat)
        if not back:
            f.paint(line([(29, 45), (28, 53)], 1) | line([(32, 45), (33, 52)], 1), ROPE, outline=False, pattern=banded())
    else:
        f.paint(belt, BROWN if t != 7 else BLACK, pattern=banded(44))
        if not back:
            buckle(f, 29, 41, M if t != 7 else GOLD, w=6, h=6)
        if not back and t >= 2:     # sickle loop on the hip
            f.paint(line([(42, 45), (42, 52)], 1), BROWN)
            f.paint(line([(41, 52), (44, 54), (46, 52), (46, 49)], 1), M, outline=False, pattern=banded())

    # --- scarf (Thorium+)
    if t >= 3:
        sc = SCARF if t not in (4, 6, 7) else ({4: BLUE_COT, 6: SILK, 7: GOLD}[t])
        f.paint(rect(23, 18, 40, 23), sc, pattern=banded(20))
        if not back:
            f.paint(poly([(33, 22), (38, 22), (37, 30), (34, 28)]), sc)
        else:
            f.paint(poly([(29, 22), (34, 22), (33, 32), (30, 30)]), sc)
    else:
        f.paint(rect(25, 18, 38, 21), shirt, pattern=banded(20))

    # --- straw hat: crown + wide brim; band in the tier colour; flower crown on Mithril
    wide = 2 if t >= 2 else 0
    hat = STRAW if t != 7 else BLACK
    brim = ell(13 - wide, 1, 50 + wide, 10)
    crown = ell(22, -8, 41, 6) & rect(22, -8, 41, 4) | rect(22, 0, 41, 4)
    if back:
        f.paint(brim, hat, pattern=weave)
        f.paint(crown, hat, pattern=weave)
    else:
        f.paint(crown, hat, pattern=weave)
        f.paint(clip(brim, y0=4), hat, pattern=weave)
        f.paint(clip(brim, y1=3) - crown, hat, pattern=weave)
    band_m = rect(22, 1, 41, 3)
    if t == 0:
        f.paint(band_m, ROPE, pattern=wrap_pat)
    else:
        f.paint(band_m, M if t != 7 else GOLD, kind='trim')
        if not back and t < 6:
            buckle(f, 34, 0, M, w=4, h=4)
    if t == 0 and not back:     # stray straw tufts
        f.dots([(14, 8, 3), (13, 9, 2), (49, 8, 3), (50, 9, 2), (25, -6, 4)], STRAW)
    if t == 6:
        for k, x in enumerate(range(23, 41, 3)):
            col = FLOWERS[k % len(FLOWERS)]
            for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
                f.set(x + dx, 2 + dy, col)
            f.set(x, 2, hx('#ffd84a') if k % 2 == 0 else hx('#ffffff'))
            f.set(x + 1, 3, hx('#3c7a22'))
    if t == 7 and not back:
        f.paint(poly([(31.5, -4), (34, 0), (31.5, 3), (29, 0)]), GOLD, kind='trim')
        f.set(31, -1, METALS['Onyxium'][3])
        f.set(32, 0, METALS['Onyxium'][2])
    return f


# ================================================================ FARMING v2 - CROP armor (Skyy LOCKED 2026-10-06)
# "start with wheat armor, and work up through the food tiers making food armor, like in skyblock"
# Same farmer look as v1 (straw hat, rolled sleeves, apron, belt, scarf, coat at the top) - now made from the crop.
WHEAT_C = ramp('#4a3a14', '#9a8040', '#b89c54', '#d2b86c', '#eAD494')    # woven wheat-straw shirt
CARROT = ramp('#3e1606', '#a8460e', '#d8661a', '#f08a34', '#ffb46a')
LEAF = ramp('#122a0e', '#2c5a1c', '#3e7a26', '#5a9c34', '#86c050')       # crop leaves / tops
CAULI = ramp('#4a4430', '#b8ae88', '#d6cea8', '#ece6c8', '#fbf8e8')      # cauliflower curd
PUMPKIN = ramp('#3a1404', '#9a440c', '#cc6a14', '#ec8e2a', '#ffbc5c')
VINE = ramp('#16240c', '#34501c', '#466a26', '#5e8a34', '#80ac4c')
CHILLI = ramp('#2e0606', '#8a1210', '#b8201a', '#de3a2a', '#ff7a5c')
DRIED = ramp('#22060a', '#4e1212', '#661c18', '#7e2a22', '#9a3e2e')     # dried-chilli maroon
BOLL = ramp('#2a1a10', '#5a3a24', '#74503a', '#8e6a50', '#a8866a')       # dry cotton bracts
ONION = ramp('#26081e', '#6a1c4a', '#8e2e66', '#b24c86', '#d47eaa')      # red-onion skin
ONION_G = ramp('#3a2008', '#8a5a1c', '#b8822e', '#dcaa4a', '#f4d68a')    # golden onion skin
ONION_T = ramp('#14081a', '#32183e', '#42214f', '#542c62', '#6a3a78')    # dark plum trousers
SAGE = ramp('#1e2a20', '#56705a', '#6e8a70', '#8aa88a', '#aac6a8')       # sage-dyed cotton shirt
ALLIUM = ramp('#2a1240', '#6a3aa0', '#8a58c4', '#ac80e0', '#d4b8f6')     # onion flower

# T, name, band (+ which metal tier's shape it echoes), crop pair on the bench step
CROPS = [
    (1, 'Wheat Armor', 'Lv 1-13  echoes Crude', 'Wheat / Lettuce'),
    (2, 'Carrot Armor', 'Lv 10-18  echoes Copper', 'Carrot / Corn'),
    (3, 'Cauliflower Armor', 'Lv 15-23  echoes Iron', 'Cauliflower / Turnip'),
    (4, 'Pumpkin Armor', 'Lv 20-28  echoes Thorium', 'Aubergine / Pumpkin'),
    (5, 'Chilli Armor', 'Lv 25-38  echoes Cobalt', 'Chilli / Tomato'),
    (6, 'Cotton Armor', 'Lv 35-43  echoes Adamantite', 'Cotton / Rice'),
    (7, 'Onion Armor', 'Lv 40-49  echoes Mithril / Onyxium', 'Onion / Potato'),
]
#        crop main, accent, shirt,   trousers,  apron,   scarf,  coat,   hat brim, hat crown
CROP_LOOK = {
    1: dict(c=STRAW, a=ROPE, shirt=WHEAT_C, tr=TROUSER, ap=None, sc=None, coat=None, brim=STRAW, crown=STRAW),
    2: dict(c=CARROT, a=LEAF, shirt=LINEN, tr=TROUSER, ap=CARROT, sc=None, coat=None, brim=STRAW, crown=CARROT),
    3: dict(c=CAULI, a=LEAF, shirt=CAULI, tr=TROUSER, ap=LEAF, sc=None, coat=None, brim=LEAF, crown=CAULI),
    4: dict(c=PUMPKIN, a=VINE, shirt=COTTON, tr=TROUSER, ap=PUMPKIN, sc=VINE, coat=None, brim=PUMPKIN, crown=PUMPKIN),
    5: dict(c=CHILLI, a=LEAF, shirt=BLUE_COT, tr=TROUSER_B, ap=DRIED, sc=CHILLI, coat=None, brim=STRAW, crown=STRAW),
    6: dict(c=COTTON, a=BOLL, shirt=SAGE, tr=TROUSER, ap=CANVAS, sc=LEAF, coat=COTTON, brim=LINEN, crown=LINEN),
    7: dict(c=ONION, a=ONION_G, shirt=LINEN, tr=ONION_T, ap=ONION_G, sc=ONION_G, coat=ONION, brim=ONION, crown=ONION),
}


def ridges(x, y, i):
    """carrot rings: a dark line every 4 rows"""
    if i in (2, 3, 4) and y % 4 == 0:
        return 1
    return i


def ribs(x, y, i):
    """pumpkin ribs: vertical grooves"""
    if i in (2, 3, 4) and x % 5 == 1:
        return 1
    if i == 2 and x % 5 == 3:
        return 3
    return i


def florets(x, y, i):
    """cauliflower curd: round bumps (5 x 5 cells, rows offset)"""
    if i == 0:
        return 0
    cy = y // 5
    u = (x + (2 if cy % 2 else 0)) % 5 - 2
    v = y % 5 - 2
    d = u * u + v * v
    if d >= 5 or (u, v) in ((2, 2), (-2, 2), (2, 1), (1, 2)):
        return 1
    if (u, v) in ((-1, -1), (0, -1), (-1, 0)):
        return 4 if i >= 2 else 3
    return 3 if i >= 3 else 2


def veins(x, y, i):
    """leaf veins: a midrib every 6 columns with side veins"""
    if i in (2, 3, 4) and (x % 6 == 2 or (x % 6 in (3, 4) and (y - x) % 6 == 0)):
        return 4 if i >= 3 else 3
    return i


def papery(x, y, i):
    """onion skin: thin vertical streaks"""
    if i in (2, 3) and x % 3 == 0 and (y // 3) % 2 == 0:
        return i + 1
    if i in (2, 3, 4) and x % 6 == 4:
        return i - 1
    return i


def cotton_weave(x, y, i):
    return fine(x, y, weave(x, y, i)) if i else 0


def wheat_ear(f, x, y, n, rp, lean=0):
    """an ear of wheat growing up from (x, y): stem + n grain pairs"""
    for k in range(n):
        cx = x + (lean * k) // 3
        cy = y - k
        f.dots([(cx, cy, 2)], rp)
        if k >= 2 and k % 2 == 0:
            f.dots([(cx - 1, cy - 1, 3), (cx + 1, cy - 1, 4 if k < n - 1 else 3)], rp)
    f.dots([(x + (lean * n) // 3, y - n, 4)], rp)


def chilli_pod(f, x, y, big=False):
    f.dots([(x, y, 2), (x + 1, y, 1)], LEAF)
    if big:     # 3 wide, 6 long, curling at the tip
        f.dots([(x - 1, y + 1, 3), (x, y + 1, 4), (x + 1, y + 1, 2), (x + 2, y + 1, 1),
                (x - 1, y + 2, 2), (x, y + 2, 4), (x + 1, y + 2, 2), (x + 2, y + 2, 1),
                (x, y + 3, 3), (x + 1, y + 3, 2), (x + 2, y + 3, 1),
                (x, y + 4, 2), (x + 1, y + 4, 1), (x + 1, y + 5, 1), (x + 2, y + 6, 0)], CHILLI)
        return
    f.dots([(x, y + 1, 4), (x + 1, y + 1, 2), (x, y + 2, 3), (x + 1, y + 2, 1), (x, y + 3, 2), (x + 1, y + 4, 1)], CHILLI)


def cotton_puff(f, x, y):
    """a cotton boll: white fluff (3 lobes) on brown bracts"""
    f.dots([(x - 2, y + 2, 1), (x + 2, y + 2, 1), (x - 1, y + 3, 0), (x, y + 3, 1), (x + 1, y + 3, 0)], BOLL)
    f.dots([(x - 1, y - 1, 4), (x, y - 1, 4), (x + 1, y - 1, 3),
            (x - 2, y, 4), (x - 1, y, 4), (x, y, 3), (x + 1, y, 3), (x + 2, y, 2),
            (x - 2, y + 1, 3), (x - 1, y + 1, 3), (x, y + 1, 2), (x + 1, y + 1, 2), (x + 2, y + 1, 1),
            (x - 1, y + 2, 2), (x, y + 2, 1), (x + 1, y + 2, 1)], COTTON)


def allium(f, x, y):
    f.dots([(x, y + k, 2) for k in range(3, 7)], LEAF)
    for dx in (-2, -1, 0, 1, 2):
        for dy in (-2, -1, 0, 1, 2):
            if abs(dx) + abs(dy) <= 3:
                i = 4 if (dx, dy) in ((-1, -1), (0, -2), (-2, 0)) else (1 if dx + dy >= 2 else (3 if (dx + dy) % 2 else 2))
                f.dots([(x + dx, y + dy, i)], ALLIUM)


def draw_crop_farmer(t, back=False):
    T, name, band, pair = CROPS[t]
    L = CROP_LOOK[T]
    C, A = L['c'], L['a']
    f = Fig()
    mannequin(f, back)
    sides = (0, 1)
    shirt, trous, coat = L['shirt'], L['tr'], L['coat']
    cpat = papery if T == 7 else cotton_weave

    # --- long coat behind (Cotton, Onion) - the v1 Adamantite+ coat shape
    if coat:
        cb = poly([(19, 21), (44, 21), (46, 68), (17, 68)])
        f.paint(cb, coat, pattern=cpat)
        if not back:
            f.paint(poly([(19, 40), (24, 40), (24, 68), (17, 68)]), coat, pattern=cpat)
            f.paint(poly([(39, 40), (44, 40), (46, 68), (39, 68)]), coat, pattern=cpat)
            f.paint(rect(24, 48, 25, 67) | rect(38, 48, 39, 67), A, outline=False)
        f.trim(bottom_rim(cb, 2), cb, A)

    # --- legs: trousers, boots
    for side in sides:
        f.paint(S(rect(21, 48, 31, 74), side), trous, pattern=fine)
        f.dots([(X(26, side), y, 1) for y in range(52, 72, 2)], trous, kind='cloth')
        if T >= 2 and not coat:      # knee patch cut from the crop
            f.paint(S(rect(23, 62, 28, 66), side), C,
                    pattern={2: ridges, 3: florets, 4: ribs}.get(T, fine))
        boot = BROWN
        bm = S(rect(21, 74, 31, 82) | rect(20, 77, 31, 82), side)
        f.paint(bm, boot, pattern=banded(80))
        f.paint(S(rect(20, 73, 31, 75), side), boot)
        if T >= 3:      # leaf / rind / skin wraps on the boot (v1: iron bands)
            f.trim(S(rect(21, 76, 31, 77), side), bm, A if T != 4 else VINE)
            f.trim(S(rect(20, 80, 31, 82), side), bm, C if T not in (3, 6) else A)
        if T >= 2:
            f.dots([(X(25, side), 74, 3), (X(25, side), 75, 1)], C)

    if coat and back:
        cs = clip(cb, y0=44)
        f.paint(cs, coat, edge_ref=cb, pattern=lambda x, y, i: 1 if i >= 2 and x in (31, 32) and y > 49 else cpat(x, y, i))
        f.trim(bottom_rim(cb, 2), cb, A)

    # --- arms: rolled sleeves, bare forearm, gloves (Cauliflower+)
    for side in sides:
        sl = S(rect(13, 22, 19, 41), side)
        f.paint(sl, coat if coat else shirt, pattern=(cpat if coat else (weave if T == 1 else fine)))
        f.paint(S(rect(12, 40, 20, 43), side), coat if coat else shirt, pattern=banded(42))
        if T >= 5:
            f.trim(S(rect(12, 42, 20, 43), side), S(rect(12, 40, 20, 43), side), C if T == 5 else A)
        if T >= 3:
            gc = {3: LEAF, 4: VINE, 5: CANVAS, 6: BOLL, 7: ONION_G}[T]
            gl = S(poly([(13, 49), (19, 49), (20, 55), (12, 55)]), side)
            f.paint(gl, gc, pattern=banded(51))
            hands(f, side, gc)
            if T >= 4:
                f.dots([(X(16, side), 50, 3), (X(16, side), 51, 1)], C)

    # --- shirt
    torso = rect(20, 21, 43, 48) | rect(21, 20, 42, 21)
    f.paint(torso, shirt if not (coat and back) else coat,
            pattern=(weave if T == 1 else (florets if T == 3 else fine)) if not (coat and back) else cpat)
    if coat and back:
        f.dots([(31, y, 0) for y in range(40, 49)] + [(32, y, 3) for y in range(40, 49)], coat, kind='cloth')
        f.trim(rect(22, 21, 41, 22), torso, A)
    if not back:
        f.paint(poly([(28, 20), (35, 20), (31.5, 27)]), shirt, pattern=lambda x, y, i: max(1, i - 1) if i else 0)
        for y in (29, 33, 37):
            f.dots([(31, y, 1), (32, y, 3)], A if T >= 3 else shirt)
    if T == 1:      # wheat sheaves tied on the shoulders
        for side in sides:
            for k, x in enumerate((13, 15, 17, 19)):
                wheat_ear(f, X(x, side), 24, 5 + k % 2, STRAW, lean=(-1 if side == 0 else 1) * (1 if k < 2 else 0))
            f.dots([(X(x, side), 24, 1) for x in range(13, 20)], ROPE)
    if coat and not back:
        for side in sides:
            lap = S(poly([(20, 21), (26, 21), (28, 34), (26, 48), (20, 48)]), side)
            f.paint(lap, coat, pattern=cpat)
            f.paint(S(line([(26, 21), (28, 34), (26, 48)], 1), side), A, outline=False)
        if T == 6:      # cotton-boll buttons
            for y in (29, 37):
                cotton_puff(f, 23, y)
                cotton_puff(f, 40, y)
        else:           # golden-skin toggles
            for y in (30, 38):
                f.dots([(23, y, 3), (24, y, 2), (39, y, 3), (40, y, 2)], ONION_G)
    if back and T >= 2 and not coat:
        for a in (line([(21, 22), (42, 42)], 2), line([(42, 22), (21, 42)], 2)):
            f.paint(a, A, outline=False, pattern=banded())
        f.dots([(31, 45, 3), (32, 45, 3), (30, 46, 1), (33, 46, 1)], A)

    # --- apron (Carrot+): the crop itself
    ap_pat = {2: ridges, 3: veins, 4: ribs, 5: fine, 6: fine, 7: papery}
    if T >= 2 and not back:
        ap = rect(25, 26, 38, 40) | rect(23, 40, 40, 64)
        ac = L['ap']
        f.paint(ap, ac, pattern=ap_pat[T])
        pk = rect(27, 50, 36, 56)
        f.paint(pk, ac, pattern=lambda x, y, i: max(1, i - 1) if i else 0)
        f.dots([(x, 50, 3) for x in range(28, 36)], ac)
        for side in sides:
            f.paint(S(line([(25, 26), (23, 20)], 2), side), A, outline=False, pattern=banded())   # leaf / stem straps
            f.dots([(X(25, side), 27, 3), (X(25, side), 28, 1)], A)
        if T >= 5:
            f.trim(bottom_rim(ap, 1) | {(x, y) for x, y in ap if x in (23, 40) and y >= 40}, ap,
                   {5: LEAF, 6: BOLL, 7: ONION}[T])
        if T == 2:      # carrot tops peeking from the pocket
            for x in (29, 31, 33):
                f.dots([(x, 49, 2), (x - 1, 48, 3), (x + 1, 47, 4), (x, 46, 3)], LEAF)
        if T == 3:      # a little cauliflower head in the pocket
            f.paint(ell(28, 45, 35, 51), CAULI, pattern=florets)
        if T == 4:      # tiny pumpkin in the pocket + a vine curl on the bib
            f.paint(ell(28, 46, 34, 51), PUMPKIN, pattern=ribs)
            f.dots([(31, 45, 2), (32, 44, 1)], VINE)
            f.dots([(28, 30, 3), (29, 29, 3), (30, 30, 2), (30, 31, 2), (29, 32, 1), (34, 31, 3), (35, 32, 2)], VINE)
        if T == 6:      # cotton bolls along the apron hem + a boll in the pocket
            for x in (26, 31, 36):
                cotton_puff(f, x, 60)
            cotton_puff(f, 31, 48)
        if T == 7:      # onion-ring emblem on the bib
            f.paint(ell(27, 28, 36, 37), ONION, outline=True)
            f.paint(ell(29, 30, 34, 35), ONION_G)
            f.paint(ell(30, 31, 33, 34), ONION, outline=False)
            f.dots([(31, 26, 2), (32, 25, 3), (31, 24, 4), (33, 24, 3)], LEAF)

    # --- chilli ristra (string of pods) across the chest, like a bandolier
    if T == 5 and not back:
        f.paint(line([(22, 21), (41, 42)], 1), ROPE, outline=False, pattern=banded())
        for x, y in ((24, 23), (28, 27), (32, 31), (36, 35)):
            chilli_pod(f, x, y, big=True)
    if T == 5 and back:
        f.paint(line([(41, 21), (22, 42)], 1), ROPE, outline=False, pattern=banded())

    # --- belt: rope with wheat ends (Wheat) -> leather with a crop buckle
    belt = rect(19, 42, 44, 45)
    if T == 1:
        f.paint(belt, ROPE, pattern=wrap_pat)
        if not back:
            f.paint(line([(29, 45), (28, 53)], 1) | line([(32, 45), (33, 52)], 1), ROPE, outline=False, pattern=banded())
            wheat_ear(f, 28, 60, 6, STRAW, lean=-1)
            wheat_ear(f, 33, 59, 6, STRAW, lean=1)
    else:
        f.paint(belt, BROWN, pattern=banded(44))
        if not back:
            buckle(f, 29, 41, C if T not in (3, 6) else A, w=6, h=6)
        if not back and T >= 3:     # sickle on the hip (tool: stays iron)
            f.paint(line([(42, 45), (42, 52)], 1), BROWN)
            f.paint(line([(41, 52), (44, 54), (46, 52), (46, 49)], 1), METALS['Iron'], outline=False, pattern=banded())

    # --- scarf (Pumpkin+)
    if L['sc']:
        sc = L['sc']
        f.paint(rect(23, 18, 40, 23), sc, pattern=banded(20))
        if not back:
            f.paint(poly([(33, 22), (38, 22), (37, 30), (34, 28)]), sc)
            if T == 4:      # vine tendril curling off the scarf
                f.dots([(38, 30, 3), (39, 31, 2), (40, 30, 2), (40, 29, 3)], VINE)
            if T == 5:
                f.dots([(35, 22, 2), (36, 22, 3)], LEAF)
        else:
            f.paint(poly([(29, 22), (34, 22), (33, 32), (30, 30)]), sc)
    else:
        f.paint(rect(25, 18, 38, 21), shirt, pattern=banded(20))

    # --- hat: the v1 straw hat, brim + crown made from the crop
    wide = {1: 0, 2: 0, 3: 2, 4: 2, 5: 3, 6: 2, 7: 2}[T]
    brim = ell(13 - wide, 1, 50 + wide, 10)
    if T == 4:
        crown = ell(21, -6, 42, 8) & rect(21, -6, 42, 4)
    elif T == 3:
        crown = ell(21, -7, 42, 8) & rect(21, -7, 42, 4)
    elif T == 2:
        crown = ell(22, -6, 41, 6) & rect(22, -6, 41, 4) | rect(22, 0, 41, 4)
    elif T == 7:
        crown = poly([(31, -7), (32, -7), (38, -3), (41, 0), (41, 4), (22, 4), (22, 0), (25, -3)])
    else:
        crown = ell(22, -8, 41, 6) & rect(22, -8, 41, 4) | rect(22, 0, 41, 4)
    bpat = {1: weave, 2: weave, 3: veins, 4: ribs, 5: weave, 6: cotton_weave, 7: papery}[T]
    cpat_h = {1: weave, 2: ridges, 3: florets, 4: ribs, 5: weave, 6: cotton_weave, 7: papery}[T]
    if back:
        f.paint(brim, L['brim'], pattern=bpat)
        f.paint(crown, L['crown'], pattern=cpat_h)
    else:
        f.paint(crown, L['crown'], pattern=cpat_h)
        f.paint(clip(brim, y0=4), L['brim'], pattern=bpat)
        f.paint(clip(brim, y1=3) - crown, L['brim'], pattern=bpat)
    if T == 3:      # leafy brim edge: notches like cauliflower leaves
        for x in range(12, 52, 4):
            if (x, 9) in brim:
                f.dots([(x, 9, 1), (x, 10, 0)], LEAF)
    band_m = rect(22, 1, 41, 3)
    band_r = {1: ROPE, 2: LEAF, 3: LEAF, 4: VINE, 5: CHILLI, 6: BOLL, 7: ONION_G}[T]
    f.paint(band_m, band_r, pattern=wrap_pat if T == 1 else banded(3), kind='trim')

    if T == 1:      # wheat ears tucked in the band + stray tufts
        if not back:
            f.dots([(14, 8, 3), (13, 9, 2), (49, 8, 3), (50, 9, 2)], STRAW)
        for k, x in enumerate((35, 37, 39)):
            wheat_ear(f, x, 2, 8 - k, STRAW, lean=1 + k)
    if T == 2:      # carrot-top leaves out of the crown
        for x, lean in ((27, -2), (30, -1), (33, 1), (36, 2)):
            for k in range(4):
                xx = x + (lean * k) // 2
                f.dots([(xx, -5 - k, 2 + (k % 2)), (xx + 1, -5 - k, 1)], LEAF)
        f.dots([(26, -8, 4), (37, -8, 4), (31, -8, 3)], LEAF)
    if T == 4:      # pumpkin stem + a leaf
        f.paint(rect(30, -8, 33, -6), VINE)
        f.dots([(34, -7, 3), (35, -8, 4), (36, -7, 3), (35, -6, 2), (36, -6, 1)], VINE)
    if T == 5:      # dried chillies hanging from the band, round the brim
        for x in ((16, 21, 26, 37, 42, 47) if not back else (16, 21, 26, 31, 37, 42, 47)):
            chilli_pod(f, x, 8 if 20 < x < 44 else 7)
    if T == 6:      # cotton bolls on the band
        for x in (24, 29, 34, 39) if not back else (26, 32, 38):
            cotton_puff(f, x, 1)
    if T == 7:      # onion sprouts from the dome tip + an allium flower in the band
        f.dots([(31, -8, 3), (32, -8, 2), (30, -8, 4)], LEAF)
        if not back:
            allium(f, 37, -3)
        f.paint(rect(22, 1, 41, 1), ONION_G, outline=False, kind='trim')
    return f


# ---------------------------------------------------------------- output
def font(n):
    return ImageFont.load_default(size=n)


def scaled(f, s):
    im = f.im.resize((W * s, (H + TOP) * s), Image.NEAREST)
    base = Image.new('RGBA', im.size, BG)
    d = ImageDraw.Draw(base)
    d.ellipse((14 * s, (79 + TOP) * s, 49 * s, (84 + TOP) * s - 1), fill=BG_SHADOW)
    base.alpha_composite(im)
    return base


def save(im, name):
    im = im.convert('RGB').quantize(colors=160, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(os.path.join(OUT, name), optimize=True)


def make_sheet(title, tiers, draw, swatch, fname, note):
    fronts = [scaled(draw(i), SCALE) for i in range(len(tiers))]
    backs = [scaled(draw(i, back=True), SCALE) for i in range(len(tiers))]
    fw, fh = fronts[0].size
    gap, top, labh = 16, 92, 50
    n = len(tiers)
    sheet_w = n * fw + (n + 1) * gap
    sheet_h = top + 2 * (fh + labh) + gap * 3
    sheet = Image.new('RGBA', (sheet_w, sheet_h), BG)
    d = ImageDraw.Draw(sheet)
    d.text((sheet_w // 2, 14), title, font=font(34), fill=INK, anchor='mt')
    d.text((sheet_w // 2, 56), note, font=font(16), fill=(60, 64, 70, 255), anchor='mt')
    for i, row in enumerate(tiers):
        name, band, mk = row[1], row[2], row[3]
        x = gap + i * (fw + gap)
        sheet.paste(fronts[i], (x, top))
        d.text((x + fw // 2, top + fh + 6), f'T{row[0]} {name}', font=font(22), fill=INK, anchor='mt')
        d.text((x + fw // 2, top + fh + 31), band + '  (front)', font=font(14), fill=(60, 64, 70, 255), anchor='mt')
        for j, col in enumerate(swatch(i)):
            d.rectangle((x + 6 + j * 16, top + 6, x + 18 + j * 16, top + 18), fill=col, outline=(30, 30, 34, 255))
        y2 = top + fh + labh + gap
        sheet.paste(backs[i], (x, y2))
        d.text((x + fw // 2, y2 + fh + 6), f'T{row[0]} {name} (back)', font=font(16), fill=(60, 64, 70, 255), anchor='mt')
    save(sheet, fname)


def main():
    def sw_m(i):
        mk = MINING[i][3]
        out = [METALS[mk][3], METALS[mk][2], METALS[mk][1]] if mk else [NONE[3], NONE[2], NONE[1]]
        if MINING[i][4]:
            out.append(hx(MINING[i][4][0]))
        return out

    def sw_f(i):
        mk = FARMING[i][3]
        shirt = {0: FIBRE, 1: LINEN, 2: LINEN, 3: COTTON, 4: BLUE_COT, 5: COTTON, 6: SILK, 7: COTTON}[i]
        return ([METALS[mk][3], METALS[mk][2], METALS[mk][1]] if mk else [ROPE[3], ROPE[2], ROPE[1]]) + [shirt[3]]

    make_sheet('SkyWynn Mining Armor ("Miner\'s gear") - concept (cloud draft)', MINING, draw_miner, sw_m,
               'mining-sheet.png', 'dark miner\'s leather + the tier metal as small plates; the helmet lamp gets brighter each tier')
    def sw_c(i):
        L = CROP_LOOK[CROPS[i][0]]
        return [L['c'][3], L['c'][2], L['c'][1], L['a'][2], L['shirt'][3]]

    if '--v1' in sys.argv:     # the replaced miner-style farming sheet, kept for comparison
        make_sheet('SkyWynn Farming Armor ("Farmer\'s clothes") - concept (cloud draft)', FARMING, draw_farmer, sw_f,
                   'farming-sheet-v1.png', 'straw hat + farm clothes (fibre -> linen -> cotton -> silk); buckles, clasps and trims in the tier metal')
    make_sheet('SkyWynn Farming Armor (crop armor) - concept v2 (cloud draft)', CROPS, draw_crop_farmer, sw_c,
               'farming-sheet.png', 'the v1 farmer look (straw hat, rolled sleeves, apron, coat) made from the crop of each Farming Bench step - wheat first')
    print('wrote mining-sheet.png + farming-sheet.png in', OUT)


if __name__ == '__main__':
    main()
