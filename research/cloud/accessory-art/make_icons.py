#!/usr/bin/env python3
"""SkyWynn booster accessories - icon concepts (cloud draft 2026-10-06).

Original pixel art, drawn from code (no copied art, no game files).
Run:  python3 research/cloud/accessory-art/make_icons.py
Writes icons/<line>-<rarity>.png (32 x 32, transparent) and accessory-sheet.png
next to this script. Deterministic: same code -> same bytes.

Same painter as research/cloud/light-armor/make_sheets.py: every icon is built
from "parts" (sets of grid pixels); each part gets a 1-px dark outline and a
4-step ramp lit from the top-left. Rarity is shown by the icon itself (rarity
frames do not render on our items in game): every line carries one gem in a
metal setting, and the gem colour = the rarity's name colour, the gem grows,
and the setting metal changes (iron -> gold -> rose gold -> platinum + glow).
"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__))
W = H = 32


def hx(s):
    s = s.lstrip('#')
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def ramp(*cols):
    """[outline, dark, mid, light, highlight]"""
    return [hx(c) for c in cols]


# ---------------------------------------------------------------- rarities
# name, name colour (VERIFIED in the spec 1.2), gem ramp, setting metal ramp
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

# ---------------------------------------------------------------- line materials
RED = ramp('#3a0a10', '#8a1422', '#c8283a', '#ec5a62', '#ffa8a8')
LEATHER = ramp('#1c1009', '#4a2c18', '#6e4426', '#946238', '#b88a5a')
LACE = ramp('#3a2a08', '#8a6a18', '#c89a2a', '#eac45a', '#fff0a0')
GLASS = ramp('#1a2a3a', '#4a6a86', '#7a9ab4', '#a8c6dc', '#e8f6ff')
MANA = ramp('#0c1a4a', '#1e3c9a', '#2e60d8', '#5a8cf0', '#a8c8ff')
CORK = ramp('#2a1a0c', '#6a4424', '#8e6034', '#b0824c', '#d2a874')
WING = ramp('#0c3a44', '#2a8a9a', '#4ac0cc', '#8ae6ee', '#dafcff')
LEAF = ramp('#0e2a12', '#24602a', '#3a8e3c', '#6cbc5a', '#b4e89a')
GRIP = ramp('#3a0c0c', '#7a1c1c', '#a83030', '#d05050', '#f08a80')
KNUCK = ramp('#1e1a1a', '#4a4040', '#6a5c58', '#8c7c74', '#b0a094')     # dark bronze
RUNE = ramp('#1a1622', '#3e3650', '#5a5070', '#7a7090', '#a49cb8')
RUNEGLOW = hx('#c070ff')
STONE = ramp('#22221f', '#555349', '#7a776a', '#a09c8c', '#c8c4b2')
BONE = ramp('#3a3020', '#9a8a68', '#c8b890', '#e6dab8', '#fff8e8')
CORD = ramp('#1a0c08', '#4a2014', '#6e3420', '#904a30', '#b06a48')
FEATHER = ramp('#3a3d48', '#9aa2b4', '#c8d0de', '#e8eef6', '#ffffff')
FLAME = ramp('#5a1a00', '#c04a00', '#ff8a1a', '#ffc84a', '#fff4b0')

INK = (34, 36, 40, 255)
BG = hx('#b4b9bf')
SLOT = hx('#2b313d')
SLOT_EDGE = hx('#454d5c')


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


# ---------------------------------------------------------------- painter
class Icon:
    def __init__(self):
        self.im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        self.px = self.im.load()

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
                self.px[x, y] = rp[i] if isinstance(i, int) else i

    def set(self, x, y, col):
        if 0 <= x < W and 0 <= y < H:
            self.px[x, y] = col


def chain(ic, pts, M):
    """chain links: alternate light / dark metal pixels along a polyline"""
    k = 0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(abs(x1 - x0), abs(y1 - y0))
        for s in range(n):
            x = round(x0 + (x1 - x0) * s / n)
            y = round(y0 + (y1 - y0) * s / n)
            ic.set(x, y, M[3] if k % 2 == 0 else M[0])
            k += 1


# ---------------------------------------------------------------- the rarity gem
def gem(ic, cx, cy, r):
    """The rarity marker: a setting (metal) + a gem (rarity colour), both grow.
    Normal 2x2 gem in a plain iron bezel; Unique 3x3 in gold; Rare 5-wide
    diamond in rose gold with 4 claws; Legendary 5x5 diamond in platinum with
    claws, then the whole icon gets an aqua halo + sparkles (see finish())."""
    _, _, G, M = RARITIES[r]
    if r == 0:
        g = rect(cx - 1, cy - 1, cx, cy)
    elif r == 1:
        g = rect(cx - 1, cy - 1, cx + 1, cy + 1)
    elif r == 2:
        g = poly([(cx, cy - 2), (cx + 2, cy), (cx, cy + 2), (cx - 2, cy)])
    else:
        g = poly([(cx, cy - 3), (cx + 3, cy), (cx, cy + 3), (cx - 3, cy)])
    bez = grow(g, 1) | (grow(g, 2) - grow(g, 1) if r >= 1 else set())
    if r == 0:
        bez = grow(g, 1)
    ic.paint(bez, M)
    if r >= 2:   # claws on the diagonals
        n = 2 if r == 2 else 3
        for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            ic.set(cx + dx * n, cy + dy * n, M[4] if dy < 0 else M[2])
    # the gem: outline-free core so even 2x2 shows colour, own dark rim on big ones
    ic.paint(g, G, outline=(r >= 2))
    # facet + specular highlight
    if r <= 1:
        ic.set(cx - 1, cy - 1, G[4])
        ic.set(cx, cy, G[1]) if r == 0 else ic.set(cx + 1, cy + 1, G[1])
        if r == 1:
            ic.set(cx, cy, G[3])
    else:
        ic.set(cx - 1, cy - 1 + (r == 2), G[4])
        ic.set(cx, cy - 1, G[3])
        ic.set(cx + 1, cy + 1, G[1])
        if r == 3:
            ic.set(cx - 1, cy - 2, G[4])
            ic.set(cx + 1, cy + 2 - 1, G[1])


def finish(ic, r):
    """Legendary only: a soft 1-px aqua halo around the icon + 3 sparkles."""
    if r < 3:
        if r == 2:   # Rare: one small pink glint
            _, _, G, _ = RARITIES[r]
            for x, y in ((27, 3), (26, 4), (28, 4), (27, 5)):
                if ic.px[x, y][3] == 0:
                    ic.set(x, y, G[3][:3] + (200,))
            ic.set(27, 4, G[4])
        return
    a = {(x, y) for x in range(W) for y in range(H) if ic.px[x, y][3] > 0}
    halo = grow(a, 1) - a
    for x, y in halo:
        ic.set(x, y, GLOW[:3] + (120,))
    _, _, G, _ = RARITIES[r]
    for sx, sy, big in ((27, 4, True), (4, 27, False), (28, 25, False)):
        if ic.px[sx, sy][3] > 130:
            continue
        ic.set(sx, sy, G[4])
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ic.set(sx + dx, sy + dy, G[3][:3] + (230,))
        if big:
            for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
                ic.set(sx + dx, sy + dy, G[3][:3] + (130,))


# ---------------------------------------------------------------- the lines
def health(ic, r):
    M = RARITIES[r][3]
    chain(ic, [(4, 2), (9, 7), (14, 9)], M)
    chain(ic, [(27, 2), (22, 7), (17, 9)], M)
    ic.paint(ring(13, 6, 18, 11, 2), M)                          # bail
    heart = ell(5, 10, 16, 21) | ell(15, 10, 26, 21) | poly([(6, 18), (25, 18), (16, 29)])
    ic.paint(heart, RED)
    ic.dots([(9, 13, 4), (8, 14, 4), (10, 13, 3)], RED)
    gem(ic, 16, 18, r)


def stamina(ic, r):
    M = RARITIES[r][3]
    ic.paint(ring(14, 1, 21, 8, 2), M)                           # hang ring
    shaft = rect(11, 7, 21, 20)
    foot = ell(8, 16, 27, 27) & rect(0, 19, 31, 27) | rect(11, 16, 21, 24)
    ic.paint(shaft | foot, LEATHER)
    ic.paint(rect(8, 25, 27, 28) & ell(7, 18, 28, 28) | rect(9, 25, 26, 27), LEATHER[:1] + LEATHER[:4])  # sole
    ic.paint(rect(10, 6, 22, 9), LEATHER)                        # cuff
    for y in (12, 15):
        ic.dots([(13, y, 4), (14, y + 1, 3), (15, y, 4), (16, y + 1, 3)], LACE)
    ic.dots([(18, 20, 3), (20, 21, 3), (22, 22, 3)], LACE)
    gem(ic, 16, 8, r)


def mana(ic, r):
    M = RARITIES[r][3]
    chain(ic, [(4, 1), (10, 4), (14, 5)], M)
    chain(ic, [(27, 1), (21, 4), (18, 5)], M)
    ic.paint(rect(13, 4, 18, 9), CORK)                           # stopper
    body = ell(7, 12, 24, 29) | rect(12, 8, 19, 15)
    ic.paint(body, GLASS)
    liquid = ell(9, 15, 22, 27) & rect(0, 18, 31, 31)
    ic.paint(liquid, MANA, outline=False)
    ic.dots([(10, 15, 4), (10, 16, 4), (11, 14, 4), (12, 22, 4), (14, 20, 4), (17, 24, 3)],
            [None, None, None, MANA[4], (240, 250, 255, 255)])
    ic.paint(rect(11, 9, 20, 12), M)                             # neck band
    gem(ic, 16, 11, r)


def speed(ic, r):
    M = RARITIES[r][3]
    # left wing, right wing (feathered steps)
    lw = poly([(13, 13), (2, 6), (3, 10), (1, 12), (4, 15), (2, 18), (8, 20), (13, 20)])
    rw = {(31 - x, y) for x, y in lw}
    for w in (lw, rw):
        ic.paint(w, WING)
    for x0, y0, x1, y1 in ((4, 10, 11, 14), (4, 15, 11, 17)):
        for p in line([(x0, y0), (x1, y1)]):
            ic.set(p[0], p[1], WING[1])
            ic.set(31 - p[0], p[1], WING[1])
    band = ring(7, 13, 24, 28, 3)
    ic.paint(band, M)
    gem(ic, 16, 25, r)


def regeneration(ic, r):
    M = RARITIES[r][3]
    ic.paint(ring(7, 13, 24, 29, 3), M)                          # the ring
    l1 = poly([(15, 13), (6, 5), (3, 8), (8, 14)])
    l2 = poly([(17, 13), (26, 5), (29, 8), (24, 14)])
    l3 = poly([(16, 11), (13, 4), (16, 1), (19, 4)])
    for l in (l1, l2, l3):
        ic.paint(l, LEAF)
    for p in line([(14, 12), (7, 7)]) | line([(18, 12), (25, 7)]) | line([(16, 10), (16, 4)]):
        ic.set(p[0], p[1], LEAF[1])
    gem(ic, 16, 14, r)


def brawler(ic, r):
    """a clenched fist in a red leather glove, metal knuckle band across it"""
    M = RARITIES[r][3]
    ic.paint(rect(10, 23, 22, 29), LEATHER)                     # wrist wrap
    for y in (25, 27):
        for x in range(11, 22):
            ic.set(x, y, LEATHER[1])
    palm = ell(6, 9, 26, 26) | rect(8, 14, 24, 24)
    ic.paint(palm, GRIP)
    for i, x0 in enumerate((6, 11, 16, 21)):                    # 4 finger knuckles
        ic.paint(ell(x0, 5, x0 + 5, 13) | rect(x0, 9, x0 + 5, 17), GRIP)
    thumb = poly([(7, 17), (19, 17), (21, 19), (19, 21), (8, 21)])
    ic.paint(thumb, GRIP)
    band = rect(6, 11, 26, 14)
    ic.paint(band, M)
    for x0 in (6, 11, 21):
        ic.dots([(x0 + 2, 12, 4)], M)
    gem(ic, 16, 12, r)


def runic(ic, r):
    M = RARITIES[r][3]
    stone = poly([(9, 4), (22, 3), (27, 10), (26, 26), (19, 29), (8, 28), (5, 18), (6, 9)])
    ic.paint(stone, RUNE)
    rune = line([(12, 13), (16, 25)]) | line([(20, 13), (16, 25)]) | line([(11, 19), (21, 19)])
    for x, y in grow(rune, 1) - rune:
        if (x, y) in stone and ic.px[x, y] != RUNE[0]:
            ic.set(x, y, RUNE[1])
    for x, y in rune:
        ic.set(x, y, RUNEGLOW)
    ic.dots([(10, 7, 4), (11, 6, 4), (8, 11, 3)], RUNE)
    gem(ic, 16, 8, r)


def stonehide(ic, r):
    M = RARITIES[r][3]
    cuff = ell(4, 4, 27, 12) | rect(4, 8, 27, 24) | ell(4, 20, 27, 28)
    ic.paint(cuff, STONE)
    ic.paint(ell(7, 5, 24, 11), STONE[:1] + [STONE[1]] * 4, outline=True)   # open top (arm hole)
    ic.paint(ell(9, 6, 22, 10), [STONE[0], STONE[0], STONE[1], STONE[0], STONE[0]], outline=False)
    for y in (14, 21):
        band = rect(4, y, 27, y + 2)
        ic.paint(band & cuff, M)
    for x in (7, 24):
        ic.dots([(x, 15, 4), (x, 22, 4)], M)
    ic.dots([(6, 18, 4), (7, 17, 3), (10, 26, 1), (12, 25, 1)], STONE)
    gem(ic, 16, 18, r)


def razorfang(ic, r):
    M = RARITIES[r][3]
    cord = line([(2, 3), (6, 9), (11, 13), (16, 14), (21, 13), (26, 9), (30, 3)], 2)
    ic.paint(cord, CORD)
    side = poly([(6, 11), (11, 13), (9, 22)])
    ic.paint(side, BONE)
    ic.paint({(31 - x, y) for x, y in side}, BONE)
    mid = poly([(12, 15), (20, 15), (16, 30)]) | rect(13, 13, 19, 16)
    ic.paint(mid, BONE)
    ic.dots([(15, 20, 4), (15, 21, 3), (15, 23, 3)], BONE)
    gem(ic, 16, 15, r)


def feather(ic, r):
    M = RARITIES[r][3]
    vane = poly([(26, 2), (29, 5), (25, 14), (17, 22), (10, 24), (9, 21), (12, 13), (19, 5)])
    ic.paint(vane, FEATHER)
    shaft = line([(27, 3), (10, 22), (5, 28)])
    for x, y in shaft:
        ic.set(x, y, FEATHER[1])
    for a, b in (((22, 6), (18, 5)), ((19, 11), (13, 11)), ((16, 16), (10, 18)),
                 ((23, 10), (26, 11)), ((19, 15), (22, 17))):
        for x, y in line([a, b]):
            if (x, y) in vane:
                ic.set(x, y, FEATHER[1])
    ic.paint(rect(5, 23, 10, 28) & ell(4, 22, 11, 29), M)      # clasp on the quill
    gem(ic, 8, 25, r)


def lantern(ic, r):
    M = RARITIES[r][3]
    ic.paint(ring(12, 0, 19, 7, 2), M)                          # hang ring
    ic.paint(poly([(9, 9), (22, 9), (19, 6), (12, 6)]) | rect(9, 8, 22, 10), M)   # cap
    ic.paint(rect(9, 25, 22, 28), M)                            # base
    glass = rect(10, 11, 21, 24)
    ic.paint(glass, GLASS)
    # warm light inside: grows with the rarity (Lantern reach grows per rarity)
    glow = ell(15 - 2 - r, 17 - 3 - r, 16 + 2 + r, 19 + 3 + r) & rect(11, 12, 20, 23)
    for x, y in glow:
        ic.set(x, y, (255, 214, 120, 255))
    flame = poly([(15, 14), (17, 17), (17, 21), (14, 21), (14, 17)])
    ic.paint(flame, FLAME)
    ic.dots([(15, 18, 4), (15, 19, 4), (16, 20, 3)], FLAME)
    for x in (9, 22):                                           # frame posts
        for y in range(11, 25):
            ic.set(x, y, M[2] if x == 9 else M[1])
    ic.dots([(9, 11, 0), (22, 24, 0)], M)
    gem(ic, 16, 9 if r < 3 else 8, r)


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
    """the icon on a dark inventory-like slot, scaled s times"""
    big = icon.resize((W * s, H * s), Image.NEAREST)
    pad = s * 2
    base = Image.new('RGBA', (big.width + 2 * pad, big.height + 2 * pad), SLOT)
    d = ImageDraw.Draw(base)
    d.rectangle((0, 0, base.width - 1, base.height - 1), outline=SLOT_EDGE, width=2)
    base.alpha_composite(big, (pad, pad))
    return base


def main():
    os.makedirs(os.path.join(OUT, 'icons'), exist_ok=True)
    S = 5
    icons = {}
    for name, _, fn in LINES:
        for r, (rn, _, _, _) in enumerate(RARITIES):
            im = make(fn, r)
            icons[name, r] = im
            im.save(os.path.join(OUT, 'icons', f'{name.lower()}-{rn.lower()}.png'), optimize=True)

    cell = slot(icons['Health', 0], S)
    cw, chh = cell.size
    left, top, gap, tiny = 250, 96, 18, 40
    colw = cw + tiny + 10
    sheet_w = left + len(RARITIES) * (colw + gap) + gap
    sheet_h = top + len(LINES) * (chh + gap) + gap + 30
    sheet = Image.new('RGBA', (sheet_w, sheet_h), BG)
    d = ImageDraw.Draw(sheet)
    d.text((sheet_w // 2, 14), 'SkyWynn Booster Accessories - icon concepts (cloud draft)', font=font(30), fill=INK, anchor='mt')
    d.text((sheet_w // 2, 52), 'rows = line, columns = rarity; each icon 32 x 32 shown 5x on a dark slot, plus 1x at the right',
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
    d.text((16, sheet_h - 24), 'Original art, generated by research/cloud/accessory-art/make_icons.py. Concept only; nothing built.',
           font=font(13), fill=(60, 64, 70, 255))
    sheet.convert('RGB').save(os.path.join(OUT, 'accessory-sheet.png'), optimize=True)
    print('icons:', len(icons), 'sheet:', sheet.size)


if __name__ == '__main__':
    main()
