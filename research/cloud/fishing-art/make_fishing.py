#!/usr/bin/env python3
"""SkyWynn fishing gear - concept icons (cloud draft 2026-10-06, v2 detail level).

Rods + reels for the 8 rod tiers (T0 Bamboo ... T7 Onyxium) and the hook /
line / sinker variants at the 4 part tiers (I-IV), all from
research/cloud/SkyyFishing-Spec-Draft.md section 4. Each icon is a 64 x 64
pixel grid (vanilla item-icon size), shown 2x on the sheet.

Metal ramps are the same colours as research/cloud/light-armor/make_sheets.py
(TIERS), so a Cobalt rod matches Cobalt light armor.

Original pixel art drawn from code (no copied art, no game files).
Run:  python3 research/cloud/fishing-art/make_fishing.py
Writes the PNGs next to this script. Deterministic: same code -> same bytes.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__))
N = 64          # icon grid
SHOW = 2        # sheet scale (128 px per icon)


def hx(s):
    s = s.lstrip('#')
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def ramp(*c):
    """[outline, dark, mid, light, highlight] - same 5-step layout as the light-armor ramps"""
    return [hx(x) for x in c]


# ---------------------------------------------------------------- palettes (metal ramps = light-armor make_sheets.py)
COPPER = ramp('#3b1a0c', '#8a4220', '#c26a34', '#e89558', '#ffc48e')
IRON = ramp('#24282e', '#5c646e', '#8e97a2', '#bcc4cc', '#eef2f5')
THORIUM = ramp('#1c3324', '#3f6b4a', '#5e9468', '#8cc08e', '#cdebc6')
COBALT = ramp('#121b3d', '#2a3f8a', '#3f63c4', '#6f95e6', '#b9d0ff')
ADAMANT = ramp('#3a0c10', '#7a1a20', '#b42c30', '#e0574f', '#ffa192')
MITHRIL = ramp('#1e3a44', '#4e8c98', '#7ec4cc', '#b4ecee', '#f2ffff')
ONYX = ramp('#160c22', '#3e2460', '#6b3fa0', '#a06cda', '#e4c8ff')
GOLD = ramp('#4a3208', '#9a6e18', '#d4a234', '#f0c860', '#fff0b0')
BAMBOO = ramp('#2e2a0e', '#7a7024', '#a89a3a', '#cfc266', '#efe6a4')
WOOD = ramp('#1f1209', '#4a2e18', '#6e4826', '#94683e', '#b88a58')
CORK = ramp('#3a2414', '#8a6038', '#b08050', '#cfa070', '#ead0a4')
LEATH = ramp('#0a090c', '#1c191f', '#2b2730', '#3f3946', '#58515f')
TWINE = ramp('#3a2e18', '#7a6640', '#a08a5c', '#c4ae80', '#e4d4ac')
RED = ramp('#3a0a0a', '#8a1a1a', '#c42c2c', '#e85a4a', '#ffa08a')
WHITE = ramp('#4a4a50', '#a8a8b0', '#cfd0d6', '#ebecf0', '#ffffff')
PAPER = ramp('#4a4338', '#b0a68e', '#d4cbb4', '#ebe4d2', '#fffdf6')
SLIME = ramp('#123a12', '#2c7a24', '#48a838', '#7ad25a', '#c4f6a0')
GLOW_PINK = hx('#ff7af0')

TIERS = [  # rod / reel tiers: name, Fishing Lv, rod max kg, reel power, metal ramp
    ('Bamboo', 'Lv 1-13', 3, 4.0, BAMBOO),
    ('Copper', 'Lv 10-18', 6, 4.9, COPPER),
    ('Iron', 'Lv 15-23', 10, 5.7, IRON),
    ('Thorium', 'Lv 20-28', 16, 6.6, THORIUM),
    ('Cobalt', 'Lv 25-38', 25, 7.6, COBALT),
    ('Adamantite', 'Lv 35-43', 40, 8.7, ADAMANT),
    ('Mithril', 'Lv 40-49', 60, 9.8, MITHRIL),
    ('Onyxium', 'Lv 40-49', 90, 11.1, ONYX),
]
# part tiers I-IV: hook metal, line fibre, sinker stone
PART_TIERS = [
    ('I', 'rod T0-T1', COPPER, ('Plant Fibre', ramp('#2a3010', '#5a6a2a', '#7f9a4a', '#a8c070', '#d4e4a4')),
     ('Cobblestone', ramp('#2a2a2c', '#5a5a5e', '#7e7e82', '#a2a2a6', '#c8c8cc'))),
    ('II', 'rod T2-T3', IRON, ('Linen', ramp('#4a4234', '#a0957a', '#c4b898', '#e0d6bc', '#faf4e2')),
     ('Sandstone', ramp('#4a3418', '#9a7440', '#c49a5c', '#e0bc80', '#f6dcaa'))),
    ('III', 'rod T4-T5', COBALT, ('Silk', ramp('#5a4a60', '#b8a8c4', '#dcd0e6', '#f2ecf8', '#ffffff')),
     ('Slate', ramp('#141c26', '#34465a', '#4c6278', '#6a8298', '#94aac0'))),
    ('IV', 'rod T6-T7', MITHRIL, ('Cindercloth', ramp('#3a1206', '#8a3010', '#c4561e', '#ec8a3a', '#ffc47a')),
     ('Basalt', ramp('#0a0a0c', '#1e1d22', '#2e2c33', '#423f48', '#5e5a66'))),
]
BG = hx('#b4b9bf')
TILE = hx('#a7adb4')
INK = (34, 36, 40, 255)


# ---------------------------------------------------------------- masks + noise
def h01(x, y, s=0):
    n = (x * 374761393 + y * 668265263 + s * 2147483647) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65535.0


def _draw(fn):
    im = Image.new('1', (N, N), 0)
    fn(ImageDraw.Draw(im))
    px = im.load()
    return {(x, y) for x in range(N) for y in range(N) if px[x, y]}


def rect(x0, y0, x1, y1):
    return {(x, y) for x in range(int(x0), int(x1) + 1) for y in range(int(y0), int(y1) + 1)}


def ell(x0, y0, x1, y1):
    return _draw(lambda d: d.ellipse((x0, y0, x1, y1), fill=1))


def ring(x0, y0, x1, y1, w):
    return _draw(lambda d: d.ellipse((x0, y0, x1, y1), outline=1, width=w))


def poly(pts):
    return _draw(lambda d: d.polygon(pts, fill=1))


def line(pts, w=1):
    return _draw(lambda d: d.line(pts, fill=1, width=w))


def arc(box, a0, a1, w):
    return _draw(lambda d: d.arc(box, a0, a1, fill=1, width=w))


# ---------------------------------------------------------------- textures
def tex_metal(seed=1):
    def f(x, y, i):
        if i == 0:
            return 0
        n = h01(x, y, seed)
        if n < 0.06:
            return max(1, i - 1)
        if n > 0.96:
            return min(4, i + 1)
        return i
    return f


def tex_grain(seed=2, every=3):
    """wood / stone grain: darker diagonal-ish streaks plus speckle"""
    def f(x, y, i):
        if i == 0:
            return 0
        if (x - y * 2 + seed) % every == 0 and h01(x, y, seed) < 0.5:
            return max(1, i - 1)
        n = h01(x, y, seed + 9)
        if n < 0.10:
            return max(1, i - 1)
        if n > 0.94:
            return min(4, i + 1)
        return i
    return f


# ---------------------------------------------------------------- painter
class Icon:
    def __init__(self):
        self.im = Image.new('RGBA', (N, N), (0, 0, 0, 0))
        self.px = self.im.load()

    def put(self, x, y, c):
        if 0 <= x < N and 0 <= y < N:
            self.px[int(x), int(y)] = c

    def paint(self, mask, rp, tex=None, outline=True, edge_ref=None):
        mask = {p for p in mask if 0 <= p[0] < N and 0 <= p[1] < N}
        if not mask:
            return
        ref = edge_ref if edge_ref is not None else mask
        edge = {(x, y) for x, y in mask
                if any(q not in ref for q in ((x, y - 1), (x - 1, y), (x + 1, y), (x, y + 1)))}
        inner = (mask - edge) if outline else mask

        def out(q):
            return q not in inner

        for (x, y) in mask:
            if outline and (x, y) in edge:
                i = 0
            else:
                up, lf, dn, rt = out((x, y - 1)), out((x - 1, y)), out((x, y + 1)), out((x + 1, y))
                if (up or lf) and (dn or rt):
                    i = 2
                elif up and lf:
                    i = 4
                elif up or lf:
                    i = 3
                elif dn or rt:
                    i = 1
                elif out((x + 2, y)) or out((x, y + 2)):
                    i = 1 if h01(x, y, 3) < 0.5 else 2
                else:
                    i = 2
            if tex:
                i = tex(x, y, i)
            self.px[x, y] = rp[i]

    def dots(self, pts, rp):
        for x, y, i in pts:
            self.put(x, y, rp[i])


def glint(ic, x, y, c=(255, 255, 255, 255)):
    for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
        ic.put(x + dx, y + dy, c)


def pips(ic, n, rp):
    """tier pips in the lower-right corner (1-4)"""
    for k in range(n):
        x = 58 - k * 4
        ic.paint(rect(x, 58, x + 2, 60), rp)


# ---------------------------------------------------------------- rods
def along(t, a=(7, 57), b=(57, 7)):
    return a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t


def seg(t0, t1, w):
    return line([along(t0), along(t1)], w)


def rod(ti):
    name, lv, kg, rp_, M = TIERS[ti]
    ic = Icon()
    bamboo = ti == 0
    # the line + bobber (drawn first, behind the rod)
    tip = along(1.0)
    ic.paint(line([tip, (tip[0], 30)], 1), WHITE, outline=False)
    bob = ell(tip[0] - 3, 29, tip[0] + 3, 37)
    ic.paint(bob, RED)
    ic.paint(rect(tip[0] - 3, 33, tip[0] + 3, 37) & bob, WHITE, edge_ref=bob)
    # blank (tapers from 5 px to 2 px), the tier metal; bamboo has nodes
    blank_mat = M if not bamboo else BAMBOO
    for k, (t0, t1, w) in enumerate(((0.30, 0.55, 6), (0.55, 0.80, 5), (0.80, 1.0, 3))):
        ic.paint(seg(t0, t1, w), blank_mat, tex=tex_metal(ti + k) if not bamboo else tex_grain(4, 5))
    if bamboo:
        for t in (0.46, 0.62, 0.78, 0.92):
            x, y = along(t)
            ic.paint(line([(x - 2, y - 2), (x + 2, y + 2)], 2), BAMBOO)
    # guides: small rings standing off the blank
    for t in (0.47, 0.64, 0.80, 0.93):
        x, y = along(t)
        g = ring(x - 1, y - 6, x + 3, y - 2, 1) | line([(x, y), (x + 1, y - 3)], 1)
        ic.paint(g, M if not bamboo else TWINE, outline=False, tex=tex_metal(7))
        ic.put(x, y - 5, (M if not bamboo else TWINE)[4])
    # tip top
    ic.paint(ell(tip[0] - 2, tip[1] - 2, tip[0] + 2, tip[1] + 2), M if not bamboo else TWINE)
    # reel seat
    ic.paint(seg(0.26, 0.34, 9), M if not bamboo else WOOD, tex=tex_metal(3))
    for t in (0.27, 0.33):
        x, y = along(t)
        ic.paint(line([(x - 4, y - 4), (x + 4, y + 4)], 1), M if not bamboo else TWINE, outline=False)
    # grip: cork for metals, twine-wrapped for bamboo, black leather for the top tiers
    grip_mat = TWINE if bamboo else (LEATH if ti >= 6 else CORK)
    ic.paint(seg(0.05, 0.27, 9), grip_mat, tex=tex_grain(ti, 3))
    for t in (0.09, 0.15, 0.21):   # wraps
        x, y = along(t)
        wrap = line([(x - 4, y - 4), (x + 4, y + 4)], 2)
        ic.paint(wrap, GOLD if ti == 7 else (M if not bamboo else TWINE))
    # butt cap
    bx, by = along(0.03)
    cap = ell(bx - 6, by - 6, bx + 6, by + 6)
    ic.paint(cap, M if not bamboo else WOOD, tex=tex_metal(ti))
    # tier flair (echo of each metal's armor shape language)
    if ti == 3:      # Thorium: chunky collar rings
        for t in (0.30, 0.34):
            x, y = along(t)
            ic.paint(ell(x - 4, y - 4, x + 4, y + 4), M, tex=tex_metal(2))
    if ti == 4:      # Cobalt: angular fin on the seat
        x, y = along(0.30)
        ic.paint(poly([(x - 2, y - 2), (x - 9, y - 9), (x + 2, y - 5)]), M)
    if ti == 5:      # Adamantite: crystal shards on the butt
        ic.paint(poly([(bx - 2, by - 3), (bx - 8, by - 11), (bx + 1, by - 6)]), M)
        ic.paint(poly([(bx + 3, by + 2), (bx + 11, by + 8), (bx + 6, by - 1)]), M)
        glint(ic, int(bx - 6), int(by - 8), M[4])
    if ti == 6:      # Mithril: small wing on the seat
        x, y = along(0.31)
        ic.paint(poly([(x - 1, y - 3), (x - 6, y - 12), (x - 3, y - 11), (x - 9, y - 16), (x + 2, y - 8)]), M)
    if ti == 7:      # Onyxium: gold-banded cap + glowing gem
        ic.paint(ring(bx - 5, by - 5, bx + 5, by + 5, 1), GOLD, outline=False)
        ic.paint(ell(bx - 2, by - 2, bx + 2, by + 2), ONYX)
        ic.put(bx, by, GLOW_PINK)
        ic.put(bx - 1, by - 1, GLOW_PINK)
    # highlight sparkle on the blank
    x, y = along(0.58)
    ic.put(x - 1, y - 1, blank_mat[4])
    return ic


# ---------------------------------------------------------------- reels
def reel(ti):
    name, lv, kg, rp_, M = TIERS[ti]
    ic = Icon()
    bamboo = ti == 0
    FR = M if not bamboo else WOOD
    LINE = WHITE if ti else TWINE
    cx, cy = 30, 34
    # mounting foot on top
    ic.paint(rect(20, 6, 40, 10), FR, tex=tex_metal(1))
    ic.paint(rect(27, 10, 33, 16), FR, tex=tex_metal(2))
    # outer frame
    fr = ell(cx - 22, cy - 22, cx + 22, cy + 22)
    ic.paint(fr, FR, tex=tex_metal(ti) if not bamboo else tex_grain(3, 4))
    # spool with wound line (rings)
    sp = ell(cx - 17, cy - 17, cx + 17, cy + 17)
    ic.paint(sp, LINE, tex=lambda x, y, i: (max(1, i - 1) if int(math.hypot(x - cx, y - cy)) % 3 == 0 and i else i))
    # spokes
    for a in (0.3, 0.3 + 2.094, 0.3 + 4.189):
        ex, ey = cx + math.cos(a) * 16, cy + math.sin(a) * 16
        ic.paint(line([(cx, cy), (ex, ey)], 3), FR, tex=tex_metal(5))
    # rivets on the rim
    for k in range(8):
        a = k * math.pi / 4 + 0.2
        x, y = int(cx + math.cos(a) * 20), int(cy + math.sin(a) * 20)
        ic.dots([(x, y, 4), (x + 1, y + 1, 1)], FR)
    # hub
    ic.paint(ell(cx - 6, cy - 6, cx + 6, cy + 6), FR if ti != 7 else GOLD, tex=tex_metal(8))
    ic.dots([(cx - 2, cy - 2, 4), (cx - 1, cy - 2, 4), (cx - 2, cy - 1, 3)], FR if ti != 7 else GOLD)
    # crank arm + knob
    arm = line([(cx, cy), (cx + 22, cy + 20)], 4)
    ic.paint(arm, FR, tex=tex_metal(9))
    kn = ell(cx + 17, cy + 15, cx + 29, cy + 27)
    ic.paint(kn, WOOD if ti < 6 else (LEATH if ti == 6 else ONYX), tex=tex_grain(2, 4))
    ic.dots([(cx + 20, cy + 18, 4)], WOOD if ti < 6 else MITHRIL)
    # loose line end
    ic.paint(line([(cx - 17, cy - 4), (4, 22), (2, 30)], 1), LINE, outline=False)
    # tier flair
    if ti == 3:
        ic.paint(ring(cx - 22, cy - 22, cx + 22, cy + 22, 3), M, tex=tex_metal(4))
    if ti == 4:
        for a in (-2.4, -0.7):
            x, y = cx + math.cos(a) * 22, cy + math.sin(a) * 22
            ic.paint(poly([(x - 3, y + 2), (x + math.cos(a) * 7, y + math.sin(a) * 7), (x + 3, y - 1)]), M)
    if ti == 5:
        for a in (-2.6, -1.6, -0.6, 2.6):
            x, y = cx + math.cos(a) * 21, cy + math.sin(a) * 21
            ic.paint(poly([(x - 2, y), (x + math.cos(a) * 8, y + math.sin(a) * 8), (x + 2, y)]), M)
    if ti == 6:
        ic.paint(poly([(cx - 20, cy - 12), (cx - 30 + 1, cy - 26), (cx - 24, cy - 24), (cx - 30 + 1, cy - 32 + 1),
                       (cx - 14, cy - 20)]), M)
    if ti == 7:
        ic.paint(ring(cx - 21, cy - 21, cx + 21, cy + 21, 1), GOLD, outline=False)
        ic.put(cx, cy, GLOW_PINK)
        ic.put(cx + 1, cy, GLOW_PINK)
    if bamboo:   # wooden pegs instead of rivets, twine binding
        ic.paint(ring(cx - 22, cy - 22, cx + 22, cy + 22, 2), TWINE, outline=False)
    return ic


# ---------------------------------------------------------------- hooks
def j_hook(ic, M, x=30, top=8, bottom=46, r=10, w=3, barb=True):
    """shank, eye, bend and point with barb; returns the eye centre"""
    ic.paint(ring(x - 4, top - 4, x + 4, top + 4, 2), M, tex=tex_metal(1))
    ic.paint(line([(x, top + 4), (x, bottom)], w), M, tex=tex_metal(2))
    ic.paint(arc((x - 2 * r + 1, bottom - r, x + 1, bottom + r), 0, 180, w), M, tex=tex_metal(3))
    px_ = x - 2 * r + 1
    ic.paint(line([(px_ + 1, bottom), (px_ + 1, bottom - 12)], w), M, tex=tex_metal(4))
    ic.paint(poly([(px_, bottom - 12), (px_ + 2, bottom - 18), (px_ + 4, bottom - 12)]), M)   # point
    if barb:
        ic.paint(poly([(px_ + 3, bottom - 10), (px_ + 8, bottom - 7), (px_ + 3, bottom - 6)]), M)
    ic.put(x - 1, top + 8, M[4])
    ic.put(x - 1, top + 9, M[4])
    return x, top


def hook(variant, pt):
    roman, rods, M, fibre, stone = PART_TIERS[pt]
    ic = Icon()
    if variant == 'Barbed Hook':
        ex, ey = j_hook(ic, M, x=38, top=10, bottom=44, r=11)
        for y in (24, 31, 38):   # extra barbs on the shank
            ic.paint(poly([(39, y), (45, y - 5), (40, y + 3)]), M)
    elif variant == 'Lost Property Hook':
        ex, ey = j_hook(ic, M, x=40, top=10, bottom=44, r=11)
        ic.paint(line([(ex, ey + 2), (30, 14), (22, 12)], 1), TWINE, outline=False)
        tg = poly([(6, 8), (20, 6), (24, 12), (21, 18), (8, 20)])
        ic.paint(tg, PAPER)
        ic.paint(ell(18, 10, 21, 13), TWINE)
        for y in (11, 14):
            ic.paint(line([(9, y), (16, y - 1)], 1), PAPER, outline=False)
            for x in range(9, 16, 2):
                ic.put(x, y, (70, 66, 80, 255))
        ic.paint(rect(8, 16, 12, 18), RED, outline=False)     # "LOST" stamp mark
    elif variant == 'Lure Hook':
        ex, ey = j_hook(ic, M, x=40, top=8, bottom=44, r=10)
        sp = poly([(44, 14), (56, 22), (58, 34), (52, 40), (46, 32)])   # spoon lure
        ic.paint(sp, GOLD if pt < 3 else M, tex=tex_metal(6))
        ic.paint(ell(50, 25, 54, 29), RED)
        glint(ic, 49, 20)
        ic.paint(line([(ex, ey), (46, 15)], 1), WHITE, outline=False)
        for k, c in enumerate((RED, WHITE, RED)):                       # feather skirt
            ic.paint(poly([(26 + k * 3, 44), (20 + k * 4, 58), (24 + k * 4, 58)]), c)
    elif variant == 'Monster Hook':
        x = 32
        ic.paint(ring(x - 5, 3, x + 5, 13, 3), M, tex=tex_metal(1))
        ic.paint(line([(x, 12), (x, 34)], 4), M, tex=tex_metal(2))
        # treble: left, right and a darker back point
        for sgn in (-1, 1):
            ic.paint(arc((x - 13 if sgn < 0 else x - 1, 26, x + 1 if sgn < 0 else x + 13, 46), 0 if sgn > 0 else 0, 180, 3), M,
                     tex=tex_metal(3))
            px_ = x - 12 if sgn < 0 else x + 12
            ic.paint(line([(px_, 36), (px_, 24)], 3), M)
            ic.paint(poly([(px_ - 2, 25), (px_, 17), (px_ + 2, 25)]), M)
            ic.paint(poly([(px_ - sgn * 1, 28), (px_ - sgn * 6, 31), (px_ - sgn * 1, 32)]), M)
        ic.paint(line([(x, 34), (x, 50)], 3), [M[0], M[0], M[1], M[1], M[2]])
        ic.paint(poly([(x - 2, 50), (x, 57), (x + 2, 50)]), M)
        for (tx, ty) in ((22, 18), (42, 18)):                              # fangs bound to the shank
            ic.paint(poly([(tx, ty), (tx + 3, ty + 10), (tx + 6, ty)]), WHITE)
        ic.paint(rect(24, 18, 40, 21), RED)
    pips(ic, pt + 1, M)
    return ic


# ---------------------------------------------------------------- lines (spools)
def spool(ic, F, M, x0=14, x1=48, y0=10, y1=52, tex=None):
    ic.paint(rect(x0 + 4, y0 + 4, x1 - 4, y1 - 4), F, tex=tex)
    for y in (y0, y1 - 5):
        ic.paint(ell(x0, y, x1, y + 6) | rect(x0 + 2, y + 1, x1 - 2, y + 5), M, tex=tex_metal(y))
    ic.paint(ell((x0 + x1) // 2 - 3, y0 + 1, (x0 + x1) // 2 + 3, y0 + 5), M)


def line_icon(variant, pt):
    roman, rods, M, (fname, F), stone = PART_TIERS[pt]
    ic = Icon()
    if variant == 'Braided Line':
        spool(ic, F, M, tex=lambda x, y, i: (max(1, i - 1) if i and ((x + y) % 6 < 2 or (x - y) % 6 < 1) else i))
        ic.paint(line([(48, 30), (56, 36), (54, 48), (60, 56)], 2), F)
    elif variant == 'Steady Line':
        spool(ic, F, M, tex=lambda x, y, i: (max(1, i - 1) if i and y % 3 == 0 else i))
        coat = rect(18, 15, 44, 47)
        for (x, y) in coat:                                               # glossy slime / sap coat
            if (x + y) % 2 == 0 and h01(x, y, 4) < 0.55:
                ic.put(x, y, SLIME[2] if h01(x, y, 5) < 0.7 else SLIME[3])
        for x, l_ in ((21, 10), (29, 15), (38, 7)):                       # drips off the flange
            ic.paint(rect(x, 15, x + 1, 15 + l_) | ell(x - 1, 14 + l_, x + 2, 18 + l_), SLIME)
            ic.put(x - 0, 16 + l_, SLIME[4])
        ic.paint(line([(48, 30), (58, 44), (58, 58)], 2), SLIME)
    elif variant == 'Twin Line':
        spool(ic, F, M, x0=4, x1=30, tex=lambda x, y, i: (max(1, i - 1) if i and y % 3 == 0 else i))
        spool(ic, RED if pt != 3 else WHITE, M, x0=32, x1=58, tex=lambda x, y, i: (max(1, i - 1) if i and y % 3 == 0 else i))
        ic.paint(line([(17, 52), (24, 60), (31, 56), (40, 60), (45, 52)], 1), F, outline=False)
    elif variant == "Scholar's Line":
        spool(ic, F, M, tex=lambda x, y, i: (max(1, i - 1) if i and y % 3 == 0 else i))
        lb = rect(16, 24, 46, 36)
        ic.paint(lb, PAPER)
        for y in (27, 30, 33):
            for x in range(19, 43):
                if h01(x, y, 5) > 0.4:
                    ic.put(x, y, (70, 66, 80, 255))
        ic.paint(poly([(46, 6), (58, 2), (60, 4), (50, 14), (47, 30), (45, 30)]), WHITE)    # quill
        ic.paint(line([(45, 30), (56, 4)], 1), PAPER, outline=False)
    pips(ic, pt + 1, M)
    return ic


# ---------------------------------------------------------------- sinkers
def sinker(variant, pt):
    roman, rods, M, fibre, (sname, ST) = PART_TIERS[pt]
    ic = Icon()
    st = tex_grain(pt + 11, 4 if pt != 1 else 3)
    if pt == 1:   # sandstone: horizontal layers
        st = lambda x, y, i: (max(1, i - 1) if i and y % 5 == 0 else tex_grain(12, 9)(x, y, i))
    if pt == 2:   # slate: flat cleaved layers
        st = lambda x, y, i: (min(4, i + 1) if i and y % 6 == 1 else (max(1, i - 1) if i and y % 6 == 0 else i))
    if variant == 'Weighted Sinker':
        ic.paint(ring(26, 3, 38, 15, 2), M, tex=tex_metal(1))
        ic.paint(poly([(32, 12), (44, 30), (48, 44), (42, 56), (22, 56), (16, 44), (20, 30)]), ST, tex=st)
        ic.paint(rect(26, 14, 38, 18), M, tex=tex_metal(2))
    elif variant == 'Clean Sinker':
        ic.paint(ring(26, 3, 38, 15, 2), M, tex=tex_metal(1))
        ic.paint(ell(12, 14, 52, 54), ST, tex=lambda x, y, i: i)    # polished: no grain
        ic.paint(ell(18, 20, 30, 30), ST, outline=False)
        glint(ic, 22, 24)
        ic.put(24, 24, (255, 255, 255, 255))
        for bx, by, r in ((54, 10, 3), (58, 22, 2), (8, 12, 2)):     # bubbles
            ic.paint(ring(bx - r, by - r, bx + r, by + r, 1), WHITE, outline=False)
            ic.put(bx - 1, by - 1, (255, 255, 255, 255))
    elif variant == 'Deep Sinker':
        ic.paint(ring(26, 1, 38, 13, 2), M, tex=tex_metal(1))
        ic.paint(poly([(26, 12), (38, 12), (46, 50), (40, 58), (24, 58), (18, 50)]), ST, tex=st)
        ic.paint(poly([(29, 28), (35, 28), (35, 40), (39, 40), (32, 48), (25, 40), (29, 40)]), M)   # down arrow inlay
        for gx, gy in ((22, 22), (42, 46)):
            glint(ic, gx, gy, hx('#d8a0ff'))                             # enchanted glint
    elif variant == 'Ember Sinker':
        ic.paint(ring(26, 3, 38, 15, 2), GOLD, tex=tex_metal(1))
        ch = poly([(30, 12), (46, 18), (52, 36), (44, 54), (22, 56), (12, 40), (16, 20)])
        ic.paint(ch, ST, tex=st)
        cr = line([(30, 16), (34, 28), (26, 38), (32, 50)], 1) | line([(34, 28), (44, 34), (48, 44)], 1) | \
            line([(26, 38), (16, 36)], 1)
        for x, y in cr:
            ic.put(x, y, hx('#ffb030') if h01(x, y, 2) > 0.3 else hx('#fff0a0'))
        for x, y in cr:
            for dx, dy in ((1, 0), (0, 1)):
                if (x + dx, y + dy) in ch and (x + dx, y + dy) not in cr:
                    ic.put(x + dx, y + dy, hx('#c43a10'))
    pips(ic, pt + 1, ST if variant != 'Ember Sinker' else GOLD)
    return ic


HOOKS = ['Barbed Hook', 'Lost Property Hook', 'Lure Hook', 'Monster Hook']
LINES = ['Braided Line', 'Steady Line', 'Twin Line', "Scholar's Line"]
SINKERS = ['Weighted Sinker', 'Clean Sinker', 'Deep Sinker']


# ---------------------------------------------------------------- output
def font(n):
    return ImageFont.load_default(size=n)


def tile(ic, s=SHOW):
    t = Image.new('RGBA', (N * s, N * s), TILE)
    t.alpha_composite(ic.im.resize((N * s, N * s), Image.NEAREST))
    return t


def save(im, name, colors=255):
    im = im.convert('RGB').quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(os.path.join(OUT, name), optimize=True)


def main():
    T = N * SHOW            # 128
    cw, gap = T + 26, 14    # cell width
    sheet_w = 2 * gap + 12 * cw + 3 * 30
    rows_h = 70 + 2 * (T + 64) + 40 + 50 + 4 * (T + 40) + 20
    sheet = Image.new('RGBA', (sheet_w, rows_h), BG)
    d = ImageDraw.Draw(sheet)
    d.text((sheet_w // 2, 14), 'SkyWynn fishing gear - rods, reels, hooks, lines, sinkers (concept icons 64 x 64, shown 2x, cloud draft)',
           font=font(30), fill=INK, anchor='mt')
    y = 70
    left = (sheet_w - 8 * cw) // 2
    for row, (fn, kind) in enumerate(((rod, 'Rod'), (reel, 'Reel'))):
        d.text((left - 6, y + T // 2), kind + 's', font=font(22), fill=INK, anchor='rm')
        for ti, (name, lv, kg, power, M) in enumerate(TIERS):
            x = left + ti * cw
            ic = fn(ti)
            sheet.paste(tile(ic), (x, y))
            ic.im.save(os.path.join(OUT, 'icons', f'{kind.lower()}-t{ti}-{name.lower()}.png'))
            d.text((x + T // 2, y + T + 6), f'T{ti} {name} {kind}', font=font(15), fill=INK, anchor='mt')
            sub = f'{lv}  |  max {kg} kg' if kind == 'Rod' else f'{lv}  |  power {power}'
            d.text((x + T // 2, y + T + 26), sub, font=font(12), fill=(60, 64, 70, 255), anchor='mt')
        y += T + 64
    d.text((sheet_w // 2, y + 8), 'Parts: one hook, one line, one sinker per rod.  Columns = part tier I (rod T0-T1) / II (T2-T3) / III (T4-T5) / IV (T6-T7); '
           'pips = tier.', font=font(17), fill=(60, 64, 70, 255), anchor='mt')
    y += 40
    groups = [('Hooks', HOOKS, hook, lambda p: PART_TIERS[p][2]), ('Lines', LINES, line_icon, lambda p: PART_TIERS[p][3][0]),
              ('Sinkers', SINKERS + ['Ember Sinker'], sinker, lambda p: PART_TIERS[p][4][0])]
    gx = gap + 10
    for gname, variants, fn, matname in groups:
        x0 = gx
        d.text((x0 + 2 * cw, y), gname, font=font(24), fill=INK, anchor='mt')
        for p in range(4):
            mat = matname(p)
            mat = mat if isinstance(mat, str) else ['Copper', 'Iron', 'Cobalt', 'Mithril'][p]
            d.text((x0 + p * cw + T // 2, y + 30), f'{PART_TIERS[p][0]}  ({mat})', font=font(13), fill=(60, 64, 70, 255), anchor='mt')
        for r, v in enumerate(variants):
            yy = y + 50 + r * (T + 40)
            for p in range(4):
                if v == 'Ember Sinker' and p != 3:
                    if p == 0:
                        d.text((x0 + 2 * cw - 20, yy + T // 2), 'stage 3: lava fishing - one item, no tiers ->',
                               font=font(14), fill=(60, 64, 70, 255), anchor='mm')
                    continue
                ic = fn(v, p)
                sheet.paste(tile(ic), (x0 + p * cw, yy))
                slug = v.lower().replace(' ', '-').replace("'", '')
                ic.im.save(os.path.join(OUT, 'icons', f'{slug}-{PART_TIERS[p][0]}.png'))
            d.text((x0 + 2 * cw - 13, yy + T + 6), v + ('  (stage 3)' if v in ('Monster Hook', 'Ember Sinker') else ''),
                   font=font(16), fill=INK, anchor='mt')
        gx += 4 * cw + 30
    save(sheet, 'fishing-gear-sheet.png')


if __name__ == '__main__':
    os.makedirs(os.path.join(OUT, 'icons'), exist_ok=True)
    main()
