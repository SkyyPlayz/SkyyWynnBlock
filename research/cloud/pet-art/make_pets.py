#!/usr/bin/env python3
"""SkyWynn Pets - concept sheet (cloud draft 2026-10-06).

Original pixel art, drawn from code (no copied art, no game files, no vanilla
creature designs - every pet is a stylised original "chibi" animal).
Run:  python3 research/cloud/pet-art/make_pets.py
Writes the PNGs next to this script. Deterministic: same code -> same bytes.

How it draws (same method as research/cloud/light-armor/make_sheets.py):
every pet is painted on a small 60 x 46 pixel grid, one "part" at a time.
Each part gets a 1-px dark outline and a 4-step shade ramp lit from the
top-left. The grid is scaled up with NEAREST so the pixels stay chunky.
Side view, facing right.
"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__))
W, H = 60, 46          # pet grid
GROUND = 42            # feet rest on this row
SCALE = 4              # sheet: 240 x 184 per pet
SOLO_SCALE = 6         # per-pet PNGs


def hx(s):
    s = s.lstrip('#')
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def ramp(*cols):
    """[outline, dark, mid, light, highlight]"""
    return [hx(c) for c in cols]


def far(rp, f=0.72):
    """darker copy of a ramp for the far-side legs / wing"""
    return [rp[0]] + [tuple(int(c * f) for c in col[:3]) + (255,) for col in rp[1:]]


# ---------------------------------------------------------------- palettes
CREAM = ramp('#3a2e22', '#b39b7c', '#d4bf9e', '#ecdcbf', '#fff6e4')
TAN = ramp('#3a2614', '#94683c', '#b88a56', '#d6ac74', '#f0d09c')
PINK = ramp('#4a2228', '#b4646e', '#d88a92', '#f0b0b4', '#ffd8da')
WHITE = ramp('#3c3a38', '#b8b2a8', '#d6d0c6', '#efeae2', '#ffffff')
RED = ramp('#3a0c0c', '#8e2020', '#c43a30', '#e66450', '#ff9c84')
YELLOW = ramp('#4a3608', '#b88a18', '#e0b42c', '#f6d65a', '#fff2a8')
GREY = ramp('#24262a', '#5e646c', '#828a92', '#a8b0b8', '#d4dade')
DGREY = ramp('#16171a', '#34373c', '#4a4e54', '#62676e', '#7e848a')
HORN = ramp('#2e2418', '#6e5a40', '#968062', '#bca88a', '#e0d0b4')
BROWN = ramp('#24160c', '#5a3820', '#7c5030', '#9e6c44', '#c08e62')
DBROWN = ramp('#160d08', '#3a2416', '#52341f', '#6c472c', '#8a5e3c')
RUST = ramp('#2a1008', '#7a3014', '#a4481e', '#c86a34', '#e8925a')
BLUEGREY = ramp('#1e2630', '#56708a', '#7896b0', '#9cbad0', '#cfe2ee')
LEATHER = ramp('#1c0e08', '#5a2a16', '#7c3c20', '#9c5430', '#c07448')
GOLD = ramp('#4a3208', '#9a6e18', '#d4a234', '#f0c860', '#fff0b0')
TEAL = ramp('#0c1e2a', '#1e4a66', '#2a6a8e', '#3c8eb4', '#7ac0de')
VIOLET = ramp('#1a0c2a', '#4a2470', '#6a3a9a', '#8e5cc4', '#c49af0')
BONE = ramp('#3a3428', '#b4a888', '#d2c6a6', '#ece2c6', '#fffaea')
WARPAINT = ramp('#3a0c0c', '#d8d0c0', '#e8e2d6', '#f4f0e8', '#ffffff')
HOOF = DGREY
EYE_K = hx('#141216')
EYE_W = hx('#ffffff')

# dragon elements: (body, belly, wing membrane)
ELEMENTS = {
    'Fire':    (ramp('#2e0a08', '#8a1e14', '#c23a1e', '#e8662c', '#ffa060'), YELLOW, ramp('#3a1008', '#a03a18', '#d86a2a', '#f49a48', '#ffc888')),
    'Earth':   (ramp('#141e0c', '#3e5a22', '#5a7e30', '#7ea044', '#b4cc7a'), TAN, ramp('#24160c', '#6a4a26', '#8e6a38', '#b08a52', '#d4b07c')),
    'Thunder': (ramp('#2a2208', '#8a6e10', '#c4a018', '#ecca30', '#fff08a'), CREAM, ramp('#14182e', '#2e3a7a', '#4a5cb0', '#7488dc', '#b0c0ff')),
    'Water':   (TEAL, ramp('#16303a', '#5aa0b0', '#80c4cc', '#a8e0e2', '#e0fafa'), ramp('#0c2232', '#1e5a7a', '#3482a8', '#5aaccc', '#9ad6ec')),
    'Air':     (ramp('#283038', '#8a9eae', '#b0c4d2', '#d4e4ee', '#f6fcff'), WHITE, ramp('#283846', '#7aa4c0', '#9cc4dc', '#c4e0f0', '#eef8ff')),
    'Blood':   (ramp('#1a0408', '#4a0a14', '#6e121e', '#94202c', '#c44450'), ramp('#2a0a0e', '#7a2a30', '#a0444a', '#c4686a', '#e8a0a0'), ramp('#1a0408', '#3a0a10', '#58121a', '#7a1e26', '#a43a40')),
    'Void':    (ramp('#0c0816', '#24183e', '#3a2660', '#56408a', '#8a72c4'), VIOLET, ramp('#06040c', '#18102a', '#281a44', '#3e2c66', '#6a52a0')),
    'Light':   (ramp('#4a3a10', '#c8b070', '#e4d090', '#f6e8b8', '#fffbe8'), WHITE, GOLD),
    'Crystal': (ramp('#1a1030', '#5a4aa8', '#7a72d4', '#a4a6f0', '#e0e8ff'), ramp('#20304a', '#7aa8d0', '#9ccaea', '#c4e6f8', '#f4ffff'), ramp('#2a1240', '#9a5ac8', '#c084e6', '#dcaaf6', '#f8e0ff')),
}

BG = hx('#b4b9bf')
BG_SHADOW = hx('#9ca2a9')
INK = (34, 36, 40, 255)
SUB = (60, 64, 70, 255)

# pet rarity colours (SkyBlock-style, see README "Questions for Skyy")
RARITY = {
    'Common': hx('#e8e8e8'), 'Uncommon': hx('#3fbf3f'), 'Rare': hx('#4060e0'),
    'Epic': hx('#a030c8'), 'Legendary': hx('#f0a018'), 'Mythic': hx('#ff4ad2'),
}


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


def line(pts, w=2):
    return _draw(lambda d: d.line(pts, fill=1, width=w))


def clip(m, y0=-99, y1=999, x0=-99, x1=999):
    return {(x, y) for x, y in m if y0 <= y <= y1 and x0 <= x <= x1}


# ---------------------------------------------------------------- painter
class Fig:
    def __init__(self, hover=0):
        self.im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        self.px = self.im.load()
        self.hover = hover      # flying pets: shadow drawn smaller

    def paint(self, mask, rp, pattern=None, outline=True):
        """Shade a part: outline on its edge, light top-left, dark bottom-right."""
        mask = {p for p in mask if 0 <= p[0] < W and 0 <= p[1] < H}
        edge = {(x, y) for x, y in mask
                if any(q not in mask for q in ((x, y - 1), (x - 1, y), (x + 1, y), (x, y + 1)))}
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

    def dots(self, pts, rp):
        for x, y, i in pts:
            if 0 <= x < W and 0 <= y < H:
                self.px[x, y] = rp[i]

    def eye(self, x, y, tall=3):
        """big cute eye: 2 wide, highlight top-left"""
        for dy in range(tall):
            for dx in range(2):
                self.px[x + dx, y + dy] = EYE_K
        self.px[x, y] = EYE_W

    def set(self, x, y, col):
        if 0 <= x < W and 0 <= y < H:
            self.px[x, y] = col


def legs(f, rp, xs, top, w=3, bottom=GROUND, hoof=None):
    for x in xs:
        f.paint(rect(x, top, x + w - 1, bottom), rp)
        if hoof:
            f.paint(rect(x, bottom - 1, x + w - 1, bottom), hoof)


def saddle(f, x0, x1, y):
    """mount marker: small leather saddle + gold trim"""
    f.paint(poly([(x0, y + 1), (x0 + 1, y - 2), (x1 - 1, y - 2), (x1, y + 1), (x1, y + 4), (x0, y + 4)]), LEATHER)
    f.paint(rect(x0 + 2, y + 4, x0 + 3, y + 8), LEATHER)          # strap
    f.dots([(x0 + 2, y + 8, 3), (x0 + 3, y + 8, 3), (x0 + 2, y - 1, 3), (x1 - 2, y - 1, 3)], GOLD)


def stripes(period, lo, hi):
    def f(x, y, i):
        return i if i == 0 else (hi if (x // period) % 2 == 0 else lo)
    return f


def wool(x, y, i):
    if i == 0:
        return 0
    k = (x * 3 + y * 5) % 7
    return 4 if k == 0 else (1 if k == 4 else max(i, 2))


# ---------------------------------------------------------------- pets
def rabbit():
    f = Fig()
    f.paint(ell(36, 6, 42, 20), far(CREAM))                        # far ear
    f.paint(ell(17, 24, 33, 42), CREAM)                            # haunch
    f.paint(ell(20, 22, 40, 41), CREAM)                            # body
    f.paint(ell(13, 25, 20, 32), WHITE)                            # tail puff
    f.paint(rect(36, 36, 40, GROUND), CREAM)                       # front paw
    f.paint(rect(22, 39, 30, GROUND), CREAM)                       # hind foot
    f.paint(ell(31, 3, 37, 19), CREAM)                             # near ear
    f.paint(ell(33, 6, 35, 15), PINK, outline=False)               # inner ear
    f.paint(ell(31, 14, 47, 30), CREAM)                            # head
    f.paint(ell(36, 24, 42, 30), WHITE, outline=False)             # cheek
    f.eye(40, 19)
    f.dots([(46, 22, 2), (46, 23, 1)], PINK)                       # nose
    f.dots([(44, 26, 0), (45, 26, 0)], CREAM)                      # mouth
    return f


def chicken():
    f = Fig()
    f.paint(poly([(19, 22), (12, 10), (16, 9), (20, 13), (21, 8), (25, 12), (25, 24)]), WHITE)   # tail
    f.paint(ell(16, 18, 42, 39), WHITE)                            # body
    f.paint(poly([(19, 25), (33, 23), (35, 27), (30, 33), (21, 33), (17, 29)]), WHITE,
            pattern=lambda x, y, i: i if i == 0 or (x + 1) % 4 else 1)   # wing
    for x in (26, 32):                                             # legs + toes
        f.paint(rect(x, 37, x + 1, GROUND), YELLOW, outline=False)
        f.paint(rect(x - 1, GROUND, x + 3, GROUND), YELLOW, outline=False)
    f.paint(poly([(36, 4), (37, 1), (39, 3), (40, 0), (42, 3), (44, 1), (45, 6), (37, 8)]), RED)  # comb
    f.paint(ell(32, 5, 46, 21), WHITE)                             # head
    f.paint(poly([(45, 11), (51, 13), (45, 16)]), YELLOW)           # beak
    f.paint(ell(43, 15, 47, 22), RED)                              # wattle
    f.eye(40, 10)
    return f


def goat():
    f = Fig()
    legs(f, far(WHITE), (19, 35), 30, hoof=HOOF)
    f.paint(poly([(13, 19), (11, 14), (15, 15), (16, 20)]), WHITE)  # tail
    f.paint(ell(13, 17, 42, 34), WHITE)                            # body
    legs(f, WHITE, (16, 38), 30, hoof=HOOF)
    f.paint(ell(34, 8, 48, 24), WHITE)                             # head
    f.paint(poly([(37, 11), (41, 9), (37, 3), (31, 0), (27, 2), (32, 4), (35, 8)]), HORN)  # horn, swept back
    f.dots([(31, 2, 1), (34, 4, 1), (37, 7, 1)], HORN)
    f.paint(ell(42, 13, 53, 23), WHITE)                            # snout
    f.paint(poly([(36, 14), (29, 16), (30, 18), (37, 17)]), far(WHITE, 0.85))   # ear
    f.paint(poly([(46, 21), (51, 22), (49, 29)]), GREY)             # beard
    f.px[44, 13] = hx('#e8c64a'); f.px[45, 13] = hx('#e8c64a')     # goat eye: yellow + bar pupil
    f.px[44, 14] = EYE_K; f.px[45, 14] = EYE_K
    f.px[44, 15] = hx('#c8a43a'); f.px[45, 15] = hx('#c8a43a')
    f.dots([(52, 16, 1), (52, 17, 1)], DGREY)
    return f


def _hog(f, body, mane, tusk, big=False, paint=False):
    legs(f, far(body), (17, 34), 31, hoof=HOOF)
    f.paint(line([(13, 21), (9, 26)], 1), body, outline=False)      # thin tail
    f.paint(ell(7, 25, 10, 28), mane)
    f.paint(ell(11, 16, 44, 36), body)                             # body
    legs(f, body, (14, 37), 31, hoof=HOOF)
    f.paint(poly([(36, 12), (52, 19), (55, 27), (52, 31), (38, 32)]), body)   # head wedge
    f.paint(rect(53, 21, 56, 28), PINK)                            # snout disc
    f.dots([(55, 23, 0), (55, 26, 0)], PINK)
    f.paint(poly([(38, 14), (36, 8), (43, 15)]), body)              # ear
    # mane strip along neck + back
    f.paint(poly([(12, 19)] + [(14 + 3 * k, (13 if big else 15) - (k % 2) * (3 if big else 2)) for k in range(10)] +
                 [(43, 15), (42, 19)]), mane)
    # warts
    f.paint(ell(45, 22, 48, 25), body)
    # tusks curving up
    if big:
        f.paint(poly([(48, 29), (52, 30), (56, 22), (54, 20), (52, 26)]), tusk)
        f.dots([(55, 21, 4), (54, 20, 4)], GOLD)
    else:
        f.paint(poly([(48, 29), (51, 30), (54, 24), (52, 23), (50, 27)]), tusk)
    f.eye(45, 17, tall=2)
    if paint:                                                      # war paint
        f.dots([(41, 21, 3), (42, 22, 3), (43, 23, 3), (40, 23, 3), (41, 24, 3), (42, 25, 3)], WARPAINT)
        f.dots([(26, 22, 3), (27, 23, 3), (28, 22, 3), (29, 23, 3), (30, 22, 3)], WARPAINT)


def warthog():
    f = Fig()
    _hog(f, GREY, DGREY, BONE)
    return f


def tusker():
    f = Fig()
    _hog(f, RUST, RED, BONE, big=True, paint=True)
    return f


def bear():
    f = Fig()
    legs(f, far(BROWN), (17, 35), 32, w=5)
    f.paint(ell(10, 14, 44, 40), BROWN)                            # body
    legs(f, BROWN, (13, 38), 32, w=6)
    f.paint(ell(36, 6, 43, 13), far(BROWN))                        # far ear
    f.paint(ell(32, 8, 51, 30), BROWN)                             # head
    f.paint(ell(31, 6, 37, 13), BROWN)                             # near ear
    f.paint(ell(32, 8, 35, 11), CREAM, outline=False)
    f.paint(ell(43, 17, 55, 28), TAN)                              # muzzle
    f.dots([(53, 18, 0), (54, 18, 0), (53, 19, 0), (54, 19, 0), (54, 19, 0)], DGREY)
    f.dots([(54, 18, 4)], DGREY)
    f.eye(43, 14)
    f.dots([(49, 25, 0), (50, 26, 0), (51, 26, 0)], TAN)
    return f


def turkey():
    f = Fig()
    # fan tail: concentric bands
    f.paint(clip(ell(3, 2, 33, 40), x1=22, y1=33), DBROWN)
    f.paint(clip(ell(6, 5, 30, 37), x1=22, y1=33), RUST, outline=False)
    f.paint(clip(ell(9, 8, 27, 34), x1=22, y1=33), TAN, outline=False)
    f.paint(clip(ell(12, 12, 24, 30), x1=22, y1=33), DBROWN, outline=False)
    for k in range(5):                                             # feather tips
        f.dots([(5 + k, 10 - k // 2 + 18 - k * 4, 4)], CREAM)
    f.paint(ell(16, 18, 41, 39), BROWN)                            # body
    f.paint(ell(20, 23, 34, 34), DBROWN, pattern=stripes(3, 2, 3))  # wing
    for x in (25, 31):
        f.paint(rect(x, 37, x + 1, GROUND), RED, outline=False)
        f.paint(rect(x - 1, GROUND, x + 3, GROUND), RED, outline=False)
    f.paint(poly([(35, 22), (38, 10), (42, 10), (41, 24)]), BLUEGREY)   # neck
    f.paint(ell(36, 5, 46, 15), BLUEGREY)                          # head
    f.paint(poly([(45, 9), (50, 11), (45, 13)]), YELLOW)            # beak
    f.paint(poly([(44, 7), (46, 7), (48, 15), (46, 16)]), RED)      # snood
    f.paint(ell(41, 12, 45, 21), RED)                              # wattle
    f.eye(41, 8, tall=2)
    return f


def wolf():
    f = Fig()
    legs(f, far(GREY), (19, 36), 30)
    f.paint(poly([(15, 21), (7, 28), (5, 37), (9, 38), (12, 32), (19, 26)]), GREY)   # bushy tail
    f.dots([(6, 36, 4), (7, 37, 4), (8, 36, 4)], WHITE)
    f.paint(ell(13, 18, 42, 33), GREY)                             # body
    legs(f, GREY, (16, 39), 30)
    f.paint(poly([(41, 12), (44, 2), (48, 11)]), far(GREY))         # far ear
    f.paint(ell(34, 8, 50, 25), GREY)                              # head
    f.paint(ell(36, 17, 46, 30), WHITE)                            # chest ruff
    f.paint(poly([(36, 11), (38, 1), (43, 10)]), GREY)              # near ear
    f.dots([(38, 5, 1), (38, 6, 1), (39, 7, 1)], PINK)
    f.paint(poly([(45, 12), (54, 16), (56, 18), (55, 20), (45, 23)]), GREY)   # tapered snout
    f.paint(poly([(46, 20), (54, 20), (46, 23)]), WHITE, outline=False)
    f.dots([(55, 17, 0), (56, 17, 0), (55, 18, 0), (56, 18, 0)], DGREY)
    f.eye(43, 12, tall=2)
    return f


def boar():
    f = Fig()
    legs(f, far(DBROWN), (18, 33), 33, w=4, hoof=HOOF)
    f.paint(line([(11, 22), (7, 24), (8, 27)], 1), DBROWN, outline=False)   # curly tail
    f.paint(ell(9, 16, 45, 39), DBROWN)                            # body
    # bristle ridge
    f.paint(poly([(12, 22)] + [(14 + 3 * k, 13 + (k % 2) * 3) for k in range(10)] + [(42, 18), (40, 22)]), BROWN)
    legs(f, DBROWN, (14, 37), 33, w=4, hoof=HOOF)
    f.paint(poly([(37, 14), (52, 22), (55, 30), (50, 34), (38, 34)]), DBROWN)   # head
    f.paint(rect(52, 23, 56, 30), PINK)                            # snout disc
    f.dots([(54, 25, 0), (54, 28, 0)], PINK)
    f.paint(poly([(40, 18), (38, 11), (45, 16)]), BROWN)            # ear
    f.paint(poly([(49, 31), (51, 32), (53, 27), (51, 27)]), BONE)   # small tusk
    f.eye(45, 20, tall=2)
    return f


def hawk():
    f = Fig()
    f.paint(rect(14, 39, 44, GROUND + 2), HORN)                     # perch log
    f.dots([(16 + 4 * k, 40, 1) for k in range(7)], HORN)
    f.paint(poly([(19, 30), (10, 41), (16, 42), (25, 34)]), BROWN, pattern=stripes(2, 1, 3))   # tail
    f.paint(ell(18, 12, 38, 38), BROWN)                            # body
    f.paint(ell(28, 15, 39, 36), CREAM, pattern=lambda x, y, i: i if i == 0 or (x + y) % 4 else 1)  # chest streaks
    f.paint(poly([(18, 15), (30, 14), (32, 24), (24, 36), (14, 38)]), DBROWN, pattern=stripes(3, 2, 3))  # wing
    for x in (28, 33):                                             # talons
        f.paint(rect(x, 36, x + 2, 40), YELLOW)
    f.paint(ell(26, 2, 42, 17), BROWN)                             # head
    f.paint(ell(32, 9, 42, 18), CREAM, outline=False)              # cheek
    f.paint(poly([(40, 6), (45, 8), (45, 13), (43, 14), (41, 11)]), YELLOW)  # hooked beak
    f.dots([(44, 13, 0), (45, 12, 0)], YELLOW)
    f.paint(rect(34, 5, 39, 6), DBROWN, outline=False)              # brow
    f.dots([(35, 7, 3), (38, 7, 3), (35, 9, 3), (38, 9, 3)], YELLOW)
    f.eye(36, 7)
    return f


def ram():
    f = Fig()
    legs(f, far(DGREY), (18, 35), 31, hoof=HOOF)
    f.paint(ell(9, 13, 45, 37), CREAM, pattern=wool)               # wool body
    legs(f, DGREY, (14, 38), 31, hoof=HOOF)
    saddle(f, 20, 31, 13)
    f.paint(ell(38, 9, 51, 26), DGREY)                             # face
    f.paint(ell(45, 15, 54, 25), DGREY)                            # muzzle
    f.paint(ell(36, 6, 44, 14), CREAM, pattern=wool)               # wool cap
    horn = ell(30, 7, 44, 21) - ell(34, 11, 40, 17)
    f.paint(horn, HORN, pattern=lambda x, y, i: i if i == 0 or (x + y) % 3 else 1)   # big curled horn
    f.paint(poly([(31, 18), (33, 23), (37, 22), (35, 19)]), HORN)
    f.eye(46, 14, tall=2)
    f.dots([(53, 18, 0), (53, 19, 0)], DGREY)
    return f


def mouflon():
    f = Fig()
    legs(f, far(RUST), (19, 35), 29, w=3, hoof=HOOF)
    f.paint(poly([(11, 19), (9, 23), (12, 24)]), RUST)              # tail
    f.paint(ell(11, 15, 44, 32), RUST)                             # body
    f.paint(clip(ell(13, 24, 42, 32), y0=27), CREAM, outline=False)  # pale belly
    f.paint(ell(18, 19, 25, 24), CREAM, outline=False)             # saddle patch
    for x in (16, 38):                                             # legs with white socks
        f.paint(rect(x, 29, x + 2, GROUND), RUST)
        f.paint(rect(x, 37, x + 2, GROUND - 1), WHITE)
        f.paint(rect(x, GROUND - 1, x + 2, GROUND), HOOF)
    saddle(f, 23, 33, 14)
    f.paint(poly([(37, 18), (41, 6), (47, 6), (45, 20)]), RUST)      # neck
    f.paint(ell(39, 2, 53, 16), RUST)                              # head
    f.paint(ell(47, 7, 56, 15), CREAM)                             # muzzle
    horn = ell(34, 1, 46, 14) - ell(37, 4, 42, 10)
    f.paint(horn, HORN, pattern=lambda x, y, i: i if i == 0 or (x - y) % 3 else 1)
    f.paint(poly([(41, 12), (44, 18), (47, 16), (44, 12)]), HORN)
    f.eye(47, 6, tall=2)
    f.dots([(55, 9, 0), (55, 10, 0)], DGREY)
    return f


def horse():
    f = Fig()
    legs(f, far(BROWN), (16, 34), 27, hoof=HOOF)
    f.paint(poly([(10, 18), (5, 26), (4, 36), (8, 34), (11, 27), (13, 20)]), DBROWN)   # tail
    f.paint(ell(8, 14, 44, 32), BROWN)                             # body
    legs(f, BROWN, (12, 37), 27, hoof=HOOF)
    f.dots([(12, 38, 4), (13, 38, 4), (14, 38, 4), (37, 38, 4), (38, 38, 4), (39, 38, 4)], WHITE)   # socks
    saddle(f, 18, 29, 13)
    f.paint(poly([(36, 20), (39, 5), (47, 4), (46, 21)]), BROWN)     # neck
    f.paint(poly([(41, 3), (51, 2), (57, 9), (57, 14), (52, 16), (44, 14)]), BROWN)  # head
    f.paint(poly([(43, 3), (44, -1), (47, 2)]), BROWN)               # ear
    f.paint(poly([(36, 18), (37, 6), (40, 1), (43, 2), (40, 8), (39, 20)]), DBROWN)   # mane
    f.paint(poly([(42, 1), (46, 0), (48, 5), (44, 6)]), DBROWN)       # forelock
    f.dots([(52, 5, 4), (53, 6, 4), (52, 6, 4)], WHITE)              # blaze
    f.eye(48, 6, tall=2)
    f.dots([(56, 11, 0), (55, 14, 0)], DBROWN)
    return f


def camel():
    f = Fig()
    legs(f, far(TAN), (16, 34), 27, w=3, hoof=HOOF)
    f.paint(poly([(9, 20), (6, 27), (8, 28)]), TAN)                 # tail
    f.paint(ell(8, 15, 42, 32), TAN)                               # body
    f.paint(ell(17, 6, 33, 24), TAN)                               # hump
    legs(f, TAN, (12, 37), 27, w=3, hoof=HOOF)
    f.dots([(12, 33, 1), (13, 33, 1), (14, 33, 1), (37, 33, 1), (38, 33, 1), (39, 33, 1)], TAN)   # knees
    # saddle blanket with desert stripes, over the hump
    f.paint(clip(ell(15, 5, 35, 25), y0=11, y1=22),
            RED, pattern=lambda x, y, i: i if i == 0 else (3 if (y // 2) % 3 == 0 else (2 if (y // 2) % 3 == 1 else 4)))
    f.dots([(16 + 2 * k, 23, 3) for k in range(9)], GOLD)
    f.paint(poly([(37, 22), (42, 10), (44, 5), (48, 6), (46, 13), (43, 24)]), TAN)   # neck
    f.paint(ell(42, 1, 55, 11), TAN)                               # head
    f.paint(ell(49, 4, 58, 12), TAN)                               # muzzle
    f.paint(poly([(43, 3), (42, 0), (45, 2)]), TAN)                  # ear
    f.dots([(46, 4, 0), (47, 4, 0)], TAN)                           # sleepy lid
    f.eye(46, 5, tall=2)
    f.dots([(57, 7, 0), (55, 10, 0), (56, 10, 0)], DBROWN)
    return f


def skrill():
    """Original 'stormwing' look (NOT the vanilla Skrill design): a hovering
    little wyvern-bird with bat wings, a spark crest and a forked tail."""
    f = Fig(hover=1)
    wing = VIOLET
    f.paint(poly([(26, 18), (16, 2), (10, 4), (6, 12), (12, 13), (16, 20)]), far(wing))   # far wing
    f.paint(line([(20, 24), (12, 28), (6, 25), (2, 30)], 2), TEAL, outline=False)   # tail
    f.paint(poly([(0, 28), (4, 26), (3, 32)]), YELLOW)                                  # spark fork
    f.paint(ell(16, 16, 36, 30), TEAL)                             # body
    f.paint(clip(ell(20, 22, 36, 30), y0=25), BLUEGREY, outline=False)   # belly
    f.paint(rect(22, 29, 23, 33), TEAL); f.paint(rect(29, 29, 30, 33), TEAL)   # tucked feet
    f.paint(poly([(28, 18), (24, 0), (16, 0), (12, 6), (18, 7), (20, 12), (22, 22)]), wing)   # near wing
    f.dots([(17, 2, 3), (20, 4, 3), (22, 8, 3), (23, 12, 3)], wing)  # wing finger
    f.paint(ell(30, 8, 44, 22), TEAL)                              # head
    f.paint(poly([(41, 14), (50, 16), (42, 20)]), YELLOW)           # beak-snout
    f.paint(poly([(32, 9), (28, 3), (31, 5), (33, 2), (35, 6), (37, 2), (38, 8)]), YELLOW)   # spark crest
    f.eye(38, 12)
    for x, y in ((47, 6), (52, 20), (8, 18), (40, 30)):            # arcane sparks
        f.dots([(x, y, 4), (x - 1, y, 3), (x + 1, y, 3), (x, y - 1, 3), (x, y + 1, 3)], YELLOW)
    return f


def dragon(element='Fire'):
    body, belly, mem = ELEMENTS[element]
    f = Fig()
    f.paint(poly([(18, 34), (8, 38), (4, 34), (2, 37), (6, 41), (16, 41), (24, 38)]), body)   # tail curl
    f.paint(poly([(2, 37), (0, 33), (4, 34)]), mem)                  # tail spade
    f.paint(poly([(24, 20), (14, 6), (10, 10), (12, 18), (18, 22)]), far(mem))   # far wing
    f.paint(ell(14, 18, 38, 41), body)                             # body (sitting)
    f.paint(ell(27, 22, 37, 40), belly, pattern=lambda x, y, i: i if i == 0 or y % 3 else 1)  # belly plates
    f.paint(rect(20, 36, 27, GROUND), body)                        # hind foot
    f.dots([(24, GROUND, 4), (26, GROUND, 4)], BONE)
    f.paint(rect(32, 33, 35, GROUND), body)                        # front leg
    f.dots([(34, GROUND, 4), (35, GROUND, 4)], BONE)
    f.paint(poly([(22, 21), (18, 4), (12, 3), (8, 8), (14, 9), (16, 16)]), mem)   # near wing
    f.paint(line([(22, 21), (18, 4)], 1), body, outline=False)
    for k in range(4):                                             # back spines
        f.paint(poly([(15 + 2 * k, 26 - 3 * k), (13 + 2 * k, 23 - 3 * k), (17 + 2 * k, 24 - 3 * k)]), mem)
    f.paint(poly([(33, 7), (27, 2), (26, 4), (31, 10)]), BONE)       # horn
    f.paint(ell(28, 4, 47, 23), body)                              # big head
    f.paint(ell(40, 10, 53, 22), body)                             # snout
    f.paint(clip(ell(41, 16, 52, 22), y0=19), belly, outline=False)  # jaw
    f.dots([(51, 13, 0), (52, 13, 0)], body)                        # nostril
    f.paint(poly([(36, 6), (35, 1), (39, 5)]), BONE)                 # small horn 2
    f.eye(39, 10, tall=4)
    f.px[40, 13] = EYE_W
    # egg shell halves at the feet
    shell = poly([(38, 36), (40, 32), (42, 35), (44, 31), (46, 35), (48, 32), (50, 36), (50, 41), (38, 41)])
    f.paint(shell, CREAM, pattern=lambda x, y, i: i if i == 0 or (x * 7 + y * 3) % 11 else 1)
    f.paint(poly([(7, 41), (8, 38), (10, 40), (12, 38), (13, 41)]), CREAM)
    if element == 'Fire':
        f.dots([(54, 14, 4), (55, 13, 3), (56, 15, 4), (55, 16, 3)], YELLOW)    # little puff of flame
    return f


# name, draw fn, family, role, zone (proposal), found-as rarity (proposal), mount?
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

ROWS = [
    ('Skill pets  (slot 1: buffs only, never fight)', ['skill']),
    ('Combat + class pets  (Summon slot: fight on foot)', ['combat', 'class']),
    ('Mounts  (Summon slot, Zone 2 stable quest) + the dragon', ['mount', 'dragon']),
]


# ---------------------------------------------------------------- output
def font(n):
    return ImageFont.load_default(size=n)


def scaled(f, s):
    im = f.im.resize((W * s, H * s), Image.NEAREST)
    base = Image.new('RGBA', im.size, BG)
    d = ImageDraw.Draw(base)
    if f.hover:
        d.ellipse((18 * s, 42 * s, 38 * s, 45 * s), fill=BG_SHADOW)
    else:
        d.ellipse((8 * s, 41 * s, 52 * s, 45 * s), fill=BG_SHADOW)
    base.alpha_composite(im)
    return base


def card(img, name, role, zone, rarity, mount, n=22):
    """pet image + rarity bar + name + role/zone line"""
    pad = 66
    out = Image.new('RGBA', (img.width, img.height + pad), BG)
    out.paste(img, (0, 0))
    d = ImageDraw.Draw(out)
    col = RARITY[rarity]
    d.rectangle((10, img.height + 2, img.width - 11, img.height + 7), fill=col, outline=(40, 42, 46, 255))
    title = name + ('  [mount]' if mount and 'Dragon' not in name else '')
    d.text((img.width // 2, img.height + 11), title, font=font(n), fill=INK, anchor='mt')
    d.text((img.width // 2, img.height + 35), f'{role}  |  {rarity}', font=font(14), fill=SUB, anchor='mt')
    d.text((img.width // 2, img.height + 51), zone, font=font(13), fill=SUB, anchor='mt')
    return out


def save(im, name):
    im = im.convert('RGB').quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(os.path.join(OUT, name), optimize=True)


def element_strip(s=2, cols=5):
    """all 9 dragon elements as small recolours (5 quest + 4 secret)"""
    names = list(ELEMENTS)
    cw, ch = W * s, H * s + 22
    rows = (len(names) + cols - 1) // cols
    out = Image.new('RGBA', (cols * cw, rows * ch), BG)
    d = ImageDraw.Draw(out)
    for i, el in enumerate(names):
        x, y = (i % cols) * cw, (i // cols) * ch
        out.paste(scaled(dragon(el), s), (x, y))
        tag = el + (' (secret)' if i >= 5 else '')
        d.text((x + cw // 2, y + H * s + 3), tag, font=font(13), fill=INK if i < 5 else SUB, anchor='mt')
    return out


def main():
    cards = {}
    for name, fn, fam, role, zone, rar, mount in PETS:
        f = fn()
        cards[name] = card(scaled(f, SCALE), name, role, zone, rar, mount)
        save(card(scaled(f, SOLO_SCALE), name, role, zone, rar, mount, n=28),
             'pet-' + name.lower().replace(' ', '-') + '.png')
    strip = element_strip()
    save(strip, 'dragon-elements.png')

    cw, chh = next(iter(cards.values())).size
    gap, top, head = 14, 64, 30
    ncol = 7
    sheet_w = ncol * cw + (ncol + 1) * gap
    sheet_h = top + len(ROWS) * (head + chh + gap) + 34
    sheet = Image.new('RGBA', (sheet_w, sheet_h), BG)
    d = ImageDraw.Draw(sheet)
    d.text((sheet_w // 2, 16), 'SkyWynn Pets - concept (cloud draft)', font=font(34), fill=INK, anchor='mt')
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
        if 'dragon' in fams:                                       # element recolours next to the hatchling
            x = gap + len(row) * (cw + gap) + 10
            d.text((x, y - 2), 'Dragon hatchling - all 9 elements (recolours of one design)',
                   font=font(15), fill=INK)
            sheet.paste(strip, (x, y + 18))
        y += chh + gap
    # rarity legend
    x = gap
    for r, col in RARITY.items():
        d.rectangle((x, y + 4, x + 26, y + 16), fill=col, outline=(40, 42, 46, 255))
        d.text((x + 32, y + 3), r, font=font(14), fill=INK)
        x += 130
    d.text((x + 20, y + 3), 'bar = rarity it is usually FOUND at (proposal); every pet can be raised with Upgrade Stones.'
           '  Zones are proposals.', font=font(14), fill=SUB)
    save(sheet, 'pet-sheet.png')


if __name__ == '__main__':
    main()
