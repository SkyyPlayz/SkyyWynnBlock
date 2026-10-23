#!/usr/bin/env python3
"""skyyitems - SkyWynn item glyphs drawn from code (our own shapes of the game's real things: pickaxe, hatchet, hoe, fishing rod,
sword, wheat, fish, flask, anvil, cooking pot, boot, map, paw, coin, compass rose). Shared by make_tiles.py and make_emblems.py.

Each glyph lives in a 32 x 32 local box centred on (0, 0), y down; Glyph(cv, cx, cy, size, angle) places it. Metal colours follow the
approved tier palette (Copper copper, Iron grey ...); wood = vanilla-like warm brown. Deterministic."""
import math

import skyypaint as P

INK = (26, 18, 24)                      # the dark outline every glyph wears
WOOD = P.hx("#8a5a34")
WOOD_D = P.hx("#5e3a1f")
IRON = P.hx("#aab3bd")
IRON_D = P.hx("#6c7782")
COPPER = P.hx("#d4824a")
GOLD = P.hx("#E8A93B")
GOLD_L = P.hx("#ffd36b")
STEEL_B = P.hx("#c9d8e6")


class Glyph(object):
    def __init__(self, cv, cx, cy, size, ang=0.0, ow=None, flip=False):
        self.cv, self.cx, self.cy = cv, cx, cy
        self.fx = -1.0 if flip else 1.0
        self.k = size / 32.0
        self.ca, self.sa = math.cos(ang), math.sin(ang)
        self.ow = ow if ow is not None else max(1.2, 1.6 * self.k)

    def T(self, pts):
        k, ca, sa = self.k, self.ca, self.sa
        fx = self.fx
        return [(self.cx + (fx * x * ca - y * sa) * k, self.cy + (fx * x * sa + y * ca) * k) for x, y in pts]

    def fill(self, pts, col, ink=True, a=1.0):
        tp = self.T(pts)
        self.cv.poly(tp, col, a)
        if ink:
            self.cv.stroke(tp, self.ow, INK, 0.9)

    def hl(self, pts, col=(255, 255, 255), a=0.35):
        self.cv.poly(self.T(pts), col, a)

    def bar(self, x0, y0, x1, y1, w, col, ink=True, dark=None):
        """a handle: a rounded bar with a highlight strip and grain bands"""
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L * w / 2.0, dx / L * w / 2.0
        quad = [(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)]
        self.fill(quad, col, ink)
        dark = dark or P.mul(col, 0.7)
        self.cv.poly(self.T([(x0 - nx * 0.2, y0 - ny * 0.2), (x1 - nx * 0.2, y1 - ny * 0.2), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)]), dark, 0.9)
        self.cv.poly(self.T([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 + nx * 0.45, y1 + ny * 0.45), (x0 + nx * 0.45, y0 + ny * 0.45)]),
                     P.mul(col, 1.3), 0.8)
        n = int(L / 4.5)
        for i in range(1, n):
            t = i / float(n)
            if (i % 2) == 0:
                cx, cy = x0 + dx * t, y0 + dy * t
                self.cv.poly(self.T([(cx + nx, cy + ny), (cx + nx + dx / L * 0.8, cy + ny + dy / L * 0.8),
                                     (cx - nx + dx / L * 0.8, cy - ny + dy / L * 0.8), (cx - nx, cy - ny)]), dark, 0.55)

    def circ(self, x, y, r, col, ink=True, a=1.0):
        pts = [(x + r * math.cos(2 * math.pi * i / 24), y + r * math.sin(2 * math.pi * i / 24)) for i in range(24)]
        self.fill(pts, col, ink, a)


# ------------------------------------------------------------------ the glyphs (local 32 x 32 box, y down)
def pickaxe(cv, cx, cy, size, ang=0.0, metal=IRON):
    g = Glyph(cv, cx, cy, size, ang)
    g.bar(0, 15, 0, -9, 3.6, WOOD)
    head = [(-15.5, -3.5), (-11, -9.5), (-4, -12.5), (0, -13), (4, -12.5), (11, -9.5), (15.5, -3.5), (13.5, -3), (8.5, -7.5), (3, -9),
            (0, -9.2), (-3, -9), (-8.5, -7.5), (-13.5, -3)]
    g.fill(head, metal)
    g.hl([(-11, -9.5), (-4, -12.5), (0, -13), (4, -12.5), (11, -9.5), (8.5, -8.6), (3, -10.6), (0, -10.8), (-3, -10.6), (-8.5, -8.6)],
         (255, 255, 255), 0.35)
    g.fill([(-2.6, -12.6), (2.6, -12.6), (2.6, -7.6), (-2.6, -7.6)], P.mul(metal, 0.72))          # the collar on the handle
    g.circ(0, -10.1, 0.9, P.mul(metal, 1.25), ink=False)


def hatchet(cv, cx, cy, size, ang=0.0, metal=IRON):
    g = Glyph(cv, cx, cy, size, ang)
    g.bar(0, 15, 0, -12, 3.6, WOOD)
    blade = [(1.2, -12.5), (6, -12.2), (10, -15), (13.5, -13), (14.5, -6.5), (13.5, 0), (10, 1.5), (6, -2.5), (1.2, -3)]
    g.fill(blade, metal)
    g.hl([(10, -15), (13.5, -13), (14.5, -6.5), (13.5, 0), (12.2, -0.4), (12.8, -6.5), (12, -12.4)], (255, 255, 255), 0.55)
    g.fill([(-2.6, -13.5), (2.4, -13.5), (2.4, -2.5), (-2.6, -2.5)], P.mul(metal, 0.72))
    g.fill([(-5.5, -11.5), (-2.6, -12), (-2.6, -4), (-5.5, -5)], P.mul(metal, 0.62))             # the poll behind


def hoe(cv, cx, cy, size, ang=0.0, metal=COPPER, flip=False):
    g = Glyph(cv, cx, cy, size, ang, flip=flip)
    g.bar(0, 15, 0, -11, 3.4, WOOD)
    g.fill([(-2.4, -14), (2.4, -14), (2.4, -9.5), (-2.4, -9.5)], P.mul(metal, 0.75))
    g.fill([(2.4, -13.8), (11.5, -12.8), (12.8, -7), (10.5, -6), (8.5, -9.6), (2.4, -10)], metal)
    g.hl([(2.4, -13.8), (11.5, -12.8), (12, -10.2), (3, -11.8)], (255, 240, 220), 0.4)


def rod(cv, cx, cy, size, ang=0.0):
    g = Glyph(cv, cx, cy, size, ang)
    bam = P.hx("#c8a35a")
    g.bar(-1.5, 15.5, 2.5, -15.5, 2.6, bam, dark=P.hx("#8d6e34"))
    for t in (0.25, 0.5, 0.75):                                  # bamboo joints
        x, y = -1.5 + 4 * t, 15.5 - 31 * t
        g.fill([(x - 2, y - 0.6), (x + 2, y - 0.6), (x + 2, y + 0.6), (x - 2, y + 0.6)], P.hx("#7a5a26"), ink=False)
    g.fill([(-2.6, 9), (0.2, 9), (0.2, 14), (-2.6, 14)], P.hx("#3b2a20"))                     # cork grip
    g.circ(-3.6, 7.5, 2.4, IRON_D)                                                              # the reel
    g.circ(-3.6, 7.5, 0.9, IRON, ink=False)
    pts = []
    for i in range(13):                                          # the line: tip -> down to the bobber
        t = i / 12.0
        pts.append((2.5 + 9 * t, -15.5 + 22 * t * t))
    g.cv.stroke(g.T(pts), max(1.0, 0.8 * g.k), (235, 240, 245), 0.9, closed=False)
    g.circ(11.5, 7.5, 2.6, P.hx("#e04a3a"))
    g.fill([(9, 7.5), (14, 7.5), (13.4, 9.4), (9.6, 9.4)], (245, 245, 245), ink=False)


def sword(cv, cx, cy, size, ang=0.0, metal=STEEL_B):
    g = Glyph(cv, cx, cy, size, ang)
    g.fill([(0, -18), (2.8, -14.5), (2.8, 4), (-2.8, 4), (-2.8, -14.5)], metal)
    g.hl([(0, -18), (-2.8, -14.5), (-2.8, 4), (-0.4, 4), (-0.4, -15)], (255, 255, 255), 0.45)
    g.fill([(-0.5, -13), (0.5, -13), (0.5, 2), (-0.5, 2)], P.mul(metal, 0.7), ink=False)          # fuller
    g.fill([(-8.5, 3.8), (8.5, 3.8), (9.5, 5.5), (8.5, 7.2), (-8.5, 7.2), (-9.5, 5.5)], GOLD)      # crossguard
    g.circ(0, 5.5, 1.4, P.hx("#4fb3e8"), ink=False)
    g.fill([(-1.7, 7.2), (1.7, 7.2), (1.7, 13.5), (-1.7, 13.5)], P.hx("#3a2620"))                # grip
    for yy in (8.6, 10.2, 11.8):
        g.fill([(-1.7, yy), (1.7, yy - 0.8), (1.7, yy - 0.2), (-1.7, yy + 0.6)], P.hx("#6b4a33"), ink=False)
    g.circ(0, 15.2, 2.2, GOLD)


def wheat(cv, cx, cy, size, ang=0.0):
    g = Glyph(cv, cx, cy, size, ang)
    gold = P.hx("#e7bf4f")
    for sx, lean in ((-4, -0.22), (0, 0.0), (4, 0.22)):
        g.bar(sx * 0.4, 15, sx + lean * 10, -4, 1.4, P.hx("#b49a3a"), ink=False)
        tx, ty = sx + lean * 10, -4
        for i in range(5):
            yy = ty - i * 3.0
            xx = tx + lean * i * 2.5
            g.fill([(xx, yy - 2.6), (xx + 1.9, yy - 0.6), (xx, yy + 1.2), (xx - 1.9, yy - 0.6)], gold)
        g.fill([(tx + lean * 12.5, ty - 16), (tx + lean * 12.5 + 0.6, ty - 13), (tx + lean * 12.5 - 0.6, ty - 13)], gold, ink=False)


def fish(cv, cx, cy, size, ang=0.0, col=None):
    g = Glyph(cv, cx, cy, size, ang)
    col = col or P.hx("#4aa3c8")
    body = [(-12, 0), (-8, -6), (0, -8), (7, -6), (11, -1.5), (11, 1.5), (7, 6), (0, 7.5), (-8, 5.5)]
    g.fill([(9, 0), (16, -7), (14.5, 0), (16, 7)], P.mul(col, 0.8))
    g.fill(body, col)
    g.hl([(-8, 1), (0, 4.5), (7, 3.5), (7, 6), (0, 7.5), (-8, 5.5)], (255, 255, 255), 0.35)
    g.fill([(-1, -7.8), (4, -11), (6, -6.2)], P.mul(col, 0.8))
    g.circ(-7.5, -1.5, 1.5, (245, 245, 245), ink=False)
    g.circ(-7.8, -1.5, 0.8, INK, ink=False)


def flask(cv, cx, cy, size, ang=0.0, liquid=None):
    g = Glyph(cv, cx, cy, size, ang)
    liquid = liquid or P.hx("#e05ab8")
    glass = (205, 230, 245)
    g.circ(0, 5, 10, glass, a=0.9)
    g.fill([(-3.4, -11), (3.4, -11), (3.4, -3.5), (-3.4, -3.5)], glass, a=0.9)
    pts = []
    for i in range(25):                                         # liquid = the lower part of the bulb
        t = math.pi * (-0.15 + 1.3 * i / 24.0)
        pts.append((8.6 * math.cos(t), 5 + 8.6 * math.sin(t)))
    g.cv.poly(g.T(pts), liquid, 1.0)
    g.cv.poly(g.T([(-7.5, 2.5), (7.5, 2.5), (7.0, 4.0), (-7.0, 4.0)]), P.mul(liquid, 1.35), 0.8)
    g.fill([(-4.2, -15), (4.2, -15), (3.8, -10.5), (-3.8, -10.5)], P.hx("#a0703e"))            # cork
    g.hl([(-6.5, -1), (-4.5, -3.5), (-3, -2), (-5, 1.5)], (255, 255, 255), 0.75)
    g.circ(2.5, 8, 1.1, (255, 255, 255), ink=False, a=0.6)
    g.circ(-1.5, 10, 0.7, (255, 255, 255), ink=False, a=0.5)


def anvil(cv, cx, cy, size, ang=0.0):
    g = Glyph(cv, cx, cy, size, ang)
    m = P.hx("#5d6670")
    body = [(-18, -7), (13, -7), (14, -2), (8, -1), (5, 2), (5, 6), (10, 9), (11, 13), (-10, 13), (-9, 9), (-5, 6), (-5, 2), (-9, -1),
            (-13, -2.5), (-17, -5)]
    g.fill(body, m)
    g.hl([(-18, -7), (13, -7), (13.4, -5), (-17.4, -5.6)], (255, 255, 255), 0.45)
    g.hl([(-5, 2), (-1.5, 2), (-1.5, 6), (-5, 6)], (255, 255, 255), 0.12)
    g.hl([(5, 2), (5, 6), (10, 9), (11, 13), (6, 13)], (0, 0, 0), 0.25)
    g.fill([(6, -7), (9, -7), (9, -5), (6, -5)], P.mul(m, 0.6), ink=False)                       # the hardy hole


def pot(cv, cx, cy, size, ang=0.0, stew=None):
    g = Glyph(cv, cx, cy, size, ang)
    stew = stew or P.hx("#8bbf4a")
    m = P.hx("#3b3f47")
    g.fill([(-8, 11), (-10, 15), (-7, 15)], m)
    g.fill([(8, 11), (10, 15), (7, 15)], m)
    bowl = [(-13, -3), (13, -3), (12.5, 4), (9, 10), (3, 12.5), (-3, 12.5), (-9, 10), (-12.5, 4)]
    g.fill(bowl, m)
    g.hl([(-12.5, -1), (-9, -1), (-8, 7), (-9, 10), (-12.5, 4)], (255, 255, 255), 0.18)
    rim = [(-14.5 + 29 * i / 20.0, -3 - 3.2 * math.sin(math.pi * i / 20.0)) for i in range(21)] + \
          [(14.5 - 29 * i / 20.0, -3 + 3.2 * math.sin(math.pi * i / 20.0)) for i in range(21)]
    g.fill(rim, P.mul(m, 1.35))
    inner = [(-12 + 24 * i / 20.0, -3 - 2.2 * math.sin(math.pi * i / 20.0)) for i in range(21)] + \
            [(12 - 24 * i / 20.0, -3 + 2.2 * math.sin(math.pi * i / 20.0)) for i in range(21)]
    g.fill(inner, stew, ink=False)
    g.circ(-4, -3.3, 1.3, P.mul(stew, 1.3), ink=False)
    g.circ(3, -2.6, 1.0, P.mul(stew, 1.3), ink=False)
    g.circ(-15, 1, 2.2, P.mul(m, 1.2))                                                           # handles
    g.circ(15, 1, 2.2, P.mul(m, 1.2))
    for sx, ph in ((-5, 0.0), (2, 1.6), (8, 3.0)):                                               # steam
        pts = [(sx + 2.0 * math.sin(ph + i * 0.9), -6 - i * 2.0) for i in range(6)]
        g.cv.stroke(g.T(pts), max(1.2, 1.5 * g.k), (235, 240, 245), 0.55, closed=False)


def boot(cv, cx, cy, size, ang=0.0):
    g = Glyph(cv, cx, cy, size, ang)
    lea = P.hx("#7a4b2a")
    g.fill([(-7, -14), (4, -14), (4, 3), (12, 5), (15, 9), (15, 12), (-8, 12), (-8, 3)], lea)
    g.fill([(-8, -14.5), (5, -14.5), (5, -10), (-8, -10)], P.hx("#c58b4a"))                      # cuff
    g.fill([(-8.5, 10), (15.5, 10), (15.5, 13.5), (-8.5, 13.5)], P.hx("#2e221c"))                 # sole
    g.hl([(-7, -10), (-4, -10), (-4, 9), (-7, 9)], (255, 255, 255), 0.18)
    for yy in (-7, -3, 1):                                                                       # laces
        g.fill([(1, yy), (5, yy - 1), (5, yy + 0.4), (1, yy + 1.4)], P.hx("#e8d7b0"), ink=False)
    g.fill([(-8, 4), (4, 4), (4, 5.5), (-8, 5.5)], GOLD, ink=False)                              # buckle strap
    g.fill([(-2, 3.2), (1.6, 3.2), (1.6, 6.3), (-2, 6.3)], GOLD_L)


def treasure_map(cv, cx, cy, size, ang=0.0):
    g = Glyph(cv, cx, cy, size, ang)
    par = P.hx("#e9d3a1")
    g.fill([(-12, -10), (12, -11), (13, 10), (-11, 11)], par)
    g.hl([(-12, -10), (12, -11), (12.2, -7), (-11.8, -6)], (255, 255, 255), 0.3)
    g.fill([(-15, -11.5), (-11, -11.5), (-10, 12), (-14, 12)], P.hx("#c9a86a"))                  # rolls
    g.fill([(11, -12.5), (15, -12.5), (16, 11), (12, 11)], P.hx("#c9a86a"))
    g.fill([(-6, 2), (-3, -4), (0, 2)], P.hx("#7d8c6a"), ink=False)                              # little peaks
    g.fill([(-2, 2), (1.5, -2.5), (4.5, 2)], P.hx("#8d9c7a"), ink=False)
    for i in range(6):                                                                           # the dotted path
        t = i / 5.0
        g.circ(-8 + 14 * t, 7 - 10 * t * t + 2 * math.sin(t * 6), 0.7, P.hx("#b8392e"), ink=False)
    g.fill([(6, -7), (9.5, -3.5), (8.5, -2.5), (5, -6)], P.hx("#b8392e"), ink=False)            # X
    g.fill([(9.5, -7), (6, -3.5), (5, -4.5), (8.5, -8)], P.hx("#b8392e"), ink=False)


def paw(cv, cx, cy, size, ang=0.0, col=None):
    g = Glyph(cv, cx, cy, size, ang)
    col = col or P.hx("#f2c27a")
    pad = [(0 + 7.5 * math.cos(2 * math.pi * i / 24), 5 + 6.2 * math.sin(2 * math.pi * i / 24) + (1.5 if math.sin(2 * math.pi * i / 24) < 0 else 0))
           for i in range(24)]
    g.fill(pad, col)
    for tx, ty, r in ((-9, -3, 3.2), (-3.5, -8.5, 3.4), (3.5, -8.5, 3.4), (9, -3, 3.2)):
        g.circ(tx, ty, r, col)
    g.hl([(-4, 1), (0, -0.5), (4, 1), (0, 2.5)], (255, 255, 255), 0.4)


def coin(cv, cx, cy, r, tilt=0.42, seed=0):
    """a gold coin seen at an angle: edge band + face + a star stamp"""
    ry = r * tilt
    cv.ellipse(cx, cy + r * 0.16, r, ry, P.hx("#9a6a1c"))
    cv.rect(cx - r, cy, 2 * r, r * 0.16, P.hx("#9a6a1c"))
    cv.ellipse(cx, cy, r, ry, GOLD)
    cv.ellipse(cx - r * 0.06, cy - ry * 0.06, r * 0.78, ry * 0.78, GOLD_L)
    cv.poly([(x, cy + (y - cy) * tilt) for x, y in P.star_pts(cx, cy, r * 0.42, 0.45, 5)], P.hx("#c98a22"), 0.85)
    cv.stroke(P.circ_pts(cx, cy, r, ry, 28), 1.2, INK, 0.55)


def compass_rose(cv, cx, cy, r, ang=0.0):
    cv.glow(cx, cy, r * 1.35, GOLD_L, 0.35)
    cv.ring(cx, cy, r * 0.70, r * 0.80, P.hx("#b07a24"))
    cv.ring(cx, cy, r * 0.72, r * 0.78, GOLD)
    for i in range(8):
        a = ang + i * math.pi / 4.0
        L = r if i % 2 == 0 else r * 0.6
        w = r * (0.16 if i % 2 == 0 else 0.12)
        tip = (cx + L * math.sin(a), cy - L * math.cos(a))
        lft = (cx + w * math.sin(a - math.pi / 2), cy - w * math.cos(a - math.pi / 2))
        rgt = (cx + w * math.sin(a + math.pi / 2), cy - w * math.cos(a + math.pi / 2))
        col = (P.hx("#d94a3a") if i == 0 else GOLD_L) if i % 2 == 0 else GOLD
        cv.poly([tip, lft, (cx, cy)], col)
        cv.poly([tip, (cx, cy), rgt], P.mul(col, 0.72))
        cv.stroke([tip, lft, (cx, cy), rgt], 1.4, INK, 0.7)
    cv.circle(cx, cy, r * 0.1, P.hx("#fff4cc"))
