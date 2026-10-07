#!/usr/bin/env python3
"""SkyWynn Mining armor v3 - HALF PLATE concept sheet (cloud draft 2026-10-07).

Original pixel art, drawn from code (no copied art, no game files, the
reference pictures stay local and were only described in words).
Run:  python3 research/cloud/gathering-armor-art/make_mining_v3.py
Writes mining-sheet-v3.png next to this script. make_sheets.py (v1) and
make_sheets_v2.py (v2) and their PNGs are NOT changed; this script imports
them read only (painter, palettes, 2x renderer, the v2 lamp).
Deterministic: same code -> same bytes.

Skyy's locks (docs/answered/gear.md, 2026-10-06):
- "id go with the half plate style ... (accept the skirt looking part.)"
  and "that armor in a half plate style, in the right metal colors"
  -> every Mining tier = half plate in ITS OWN metal: big rounded embossed
  pauldrons, sculpted segmented breastplate, layered plate arms +
  gauntlets, crossed leather straps + buckled belts, plated greaves +
  boots, NO skirt / tabard.
- Keep the v2 helmets (Skyy likes the heads) and the lamp; a lamp that
  shows must REALLY light (SkyyAccessories Lantern code).
- Mining starts at Copper; Mithril / Onyxium are staged (drawn, marked).
- 2x-4x the v1 detail.

How the detail is made: the shapes are laid out on the v1 64 x 84 grid,
rendered at 2x (128 x 168) by the v2 ramp-aware upscaler (EPX corners,
1-px outlines, bevels, metal / leather / cloth texture), then a FINE pass
paints straight onto the 2x grid: embossed scrolls + raised rims on the
pauldrons, the sculpted chest (centre ridge + pec curves), lame edge
highlights, 2x rivets, greave ridges, knuckle studs, scratches and
patina flecks (verdigris on Copper, rust on Iron). Shown at x3.
"""
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_sheets as m        # noqa: E402  (v1, read only)
import make_sheets_v2 as v2    # noqa: E402  (v2, read only; patches m.Fig -> Fig2)
from PIL import Image, ImageDraw  # noqa: E402

hx, ramp, mix = m.hx, m.ramp, m.mix
rect, ell, poly, line, clip, S, X = m.rect, m.ell, m.poly, m.line, m.clip, m.S, m.X
bottom_rim, top_rim, mirror = m.bottom_rim, m.top_rim, m.mirror
TOPR = 12
m.TOP = TOPR

# cloth / sash ramps (new)
TEAL = ramp('#0a1c1c', '#1c4a48', '#2a6662', '#3c8680', '#5eaaa2')       # Copper sash (verdigris teal)
RUST = ramp('#240a06', '#5a1e10', '#7c2c18', '#a04224', '#c86438')       # Iron / Cobalt sash (rust-ember)
CHAR = ramp('#0c0a0a', '#221e1e', '#302a2a', '#403838', '#564c4a')       # Adamantite sash (charcoal)
for _r, _m in ((TEAL, 'cloth'), (RUST, 'cloth'), (CHAR, 'cloth')):
    v2.MATS[tuple(_r)] = _m
GAMB = m.LEATHER                     # dark padded undersuit between the plates
STRAP = m.BROWN                      # leather straps + belts

TIERS = [  # name, band, metal key, lamp (colour, strength), sash, wear (colour or None), staged
    ('Copper Miner', 'Lv 10-18', 'Copper', ('#ffd27a', 0.45), TEAL, '#4fa58a', False),
    ('Iron Miner', 'Lv 15-23', 'Iron', ('#ffe49a', 0.55), RUST, '#9a4a24', False),
    ('Thorium Miner', 'Lv 20-28', 'Thorium', ('#fff2b4', 0.70), m.SAND, None, False),
    ('Cobalt Miner', 'Lv 25-38', 'Cobalt', ('#d8ecff', 0.80), RUST, None, False),
    ('Adamantite Miner', 'Lv 35-43', 'Adamantite', ('#fff0c8', 0.90), CHAR, None, False),
    ('Mithril Miner', 'Lv 40-49', 'Mithril', ('#e6ffff', 1.0), v2.STORM, None, True),
    ('Onyxium Miner', 'Lv 40-49 (50+ later)', 'Onyxium', ('#ff8af2', 1.0), v2.ONYX, None, True),
]


def rv(f, x, y, side, M):
    m.rivet(f, X(x, side) - (1 if side else 0), y, M)


# ================================================================ the v2 helmets (unchanged designs)
def helmet(f, T, M, back, lp):
    """copied from make_sheets_v2.draw_miner2 (T 2..7) + the v1 Copper hard hat (T 1)"""
    sides = (0, 1)
    L = m.LEATHER
    lx, ly = 31, -2
    if T == 1:      # v1 Copper Miner hard hat
        dome = ell(20, -4, 43, 14) & rect(19, -8, 44, 6)
        f.paint(dome, M, kind='trim')
        f.paint(rect(18, 5, 45, 7), M, kind='trim')
        if back:
            f.paint(rect(22, 8, 41, 9), m.BROWN)
        lx, ly = 31, 0
    elif T == 2:    # mail coif + kettle hat
        coif = rect(21, 4, 42, 22)
        if not back:
            coif = coif - (ell(24, 4, 39, 21) & rect(24, 6, 39, 21))
        f.paint(coif, M, pattern=v2.mail, kind='trim')
        f.paint(ell(21, -7, 42, 12) & rect(20, -8, 43, 3), M, pattern=m.banded(-1), kind='trim')
        f.paint(poly([(14, 7), (19, 3), (44, 3), (49, 7), (47, 9), (16, 9)]), M, kind='trim')
        for x in (23, 27, 36, 40):
            m.rivet(f, x, 1, M)
    elif T == 3:    # turban-wrapped cone helm + havelock + face scarf
        if back:
            f.paint(poly([(20, 2), (43, 2), (46, 22), (17, 22)]), m.SAND, pattern=v2.folds)
        else:
            for side in sides:
                f.paint(S(poly([(19, 4), (23, 4), (24, 20), (18, 22)]), side), m.SAND, pattern=v2.folds)
            f.paint(rect(23, 12, 40, 19), m.SAND, pattern=m.banded(14, 17))
        cone = poly([(31.5, -12), (37, -5), (42, 2), (42, 5), (21, 5), (21, 2), (26, -5)])
        f.paint(cone, M, pattern=lambda x, y, i: 1 if i in (2, 3) and x in (26, 31, 37) else i, kind='trim')
        f.paint(rect(19, 1, 44, 6), m.SAND, pattern=m.wrap_pat)
        lx, ly = 31, -3
    elif T == 4:    # angular helm, fur ring, goggles
        helm = poly([(20, 7), (21, -1), (25, -6), (38, -6), (42, -1), (43, 7)])
        f.paint(helm, M, pattern=v2.chevrons, kind='trim')
        f.paint(rect(30, -7, 33, 6), M, kind='trim')
        ring = ((ell(19, 2, 44, 23) - ell(23, 6, 40, 21)) & rect(18, 4, 45, 21) if not back
                else poly([(20, 3), (43, 3), (46, 22), (17, 22)]))
        f.paint(ring, v2.FUR)
        if not back:
            f.paint(rect(24, 9, 39, 12), L)
            for gx in (25, 33):
                f.paint(ell(gx, 8, gx + 5, 13), M, kind='trim')
                for (x, y) in ell(gx + 1, 9, gx + 4, 12):
                    v2.gpx(f, x, y, mix(M[3], hx('#9ad0ff'), 0.6))
                v2.gpx(f, gx + 1, 9, hx('#ffffff'))
        lx, ly = 31, -1
    elif T == 5:    # closed horned great-helm, T slit (Skyy: "i like the head")
        for side in sides:
            f.paint(S(poly([(21, 1), (16, -2), (12, -8), (13, -12), (17, -6), (23, -3)]), side),
                    ramp('#2a2420', '#6e6458', '#8e8476', '#b0a696', '#d6ccbc'), kind='trim')
        gh = poly([(20, -1), (24, -6), (39, -6), (43, -1), (44, 18), (19, 18)])
        f.paint(gh, M, pattern=m.banded(4, 14), kind='trim')
        f.paint(rect(30, -8, 33, -1), M, kind='trim')
        if not back:
            for (x, y) in rect(22, 7, 41, 8) | rect(30, 9, 33, 14):
                v2.gpx(f, x, y, mix(hx('#140404'), v2.EMBER, 0.35 if y > 8 else 0.15))
            f.dots([(x, 16, 1) for x in (24, 26, 37, 39)], M)
        lx, ly = 31, 1
    elif T == 6:    # winged helm
        feathers = ([(21, 4), (13, 3), (6, 5), (11, 7), (21, 8)],
                    [(21, 1), (12, -2), (4, -3), (8, 1), (14, 3), (21, 5)],
                    [(21, -2), (14, -7), (6, -12), (9, -7), (14, -3), (21, 2)])
        for side in sides:
            for pts in feathers:
                fm = S(poly(pts), side)
                f.paint(fm, M, kind='trim')
                spine = {(x, y) for x, y in fm if (x, y + 1) in fm and (x, y - 1) in fm and (x, y + 2) not in fm}
                f.dots([(x, y, 4) for x, y in spine if (x, y) in fm], M)
        dome = ell(20, -6, 43, 16) & rect(19, -8, 44, 8)
        f.paint(dome, M, pattern=v2.arcs, kind='trim')
        f.paint(rect(20, 6, 43, 8), M, kind='trim')
        for side in sides:
            f.paint(S(poly([(20, 8), (25, 8), (25, 15), (22, 18), (20, 17)]), side), M, kind='trim')
        if back:
            f.paint(rect(20, 8, 43, 18), M, pattern=m.banded(12, 15), kind='trim')
        else:
            f.paint(rect(31, 8, 32, 13), M, kind='trim')
        f.paint(poly([(30, 5), (30, -8), (31.5, -11), (33, -8), (33, 5)]), M, kind='trim')
        lx, ly = 31, 0
    elif T == 7:    # onyx crown helm with crystal points
        for cx, hgt in ((23, 5), (27, 8), (31.5, 11), (36, 8), (40, 5)):
            f.paint(poly([(cx - 2, 0), (cx, -hgt - 1), (cx + 2, 0)]), v2.CRYSTAL, kind='trim')
        dome = ell(20, -5, 43, 14) & rect(19, -6, 44, 7)
        f.paint(dome, M, kind='trim')
        f.paint(rect(19, 4, 44, 7), m.GOLD, kind='trim')
        for side in sides:
            f.paint(S(poly([(20, 7), (24, 7), (25, 14), (22, 17), (20, 15)]), side), m.GOLD, kind='trim')
        if back:
            f.paint(rect(20, 7, 43, 17), M, kind='trim')
        lx, ly = 31, 0
    if not back:
        v2.lamp(f, lx, ly, lp[0], lp[1], M if T >= 3 else m.BROWN)


# ================================================================ half plate body (64 grid)
def pauldron_masks(side):
    """big round pauldron: dome + 2 lames below (left side, then mirrored)"""
    dome = ell(5, 15, 24, 32) & rect(0, 0, 63, 29)
    l1 = clip(ell(7, 21, 22, 35), y0=29)
    l2 = clip(ell(9, 24, 20, 37), y0=33)
    return S(dome, side), S(l1, side), S(l2, side)


def draw_miner3(t, back=False):
    name, band, mk, lp, sash, wear, staged = TIERS[t]
    M = m.METALS[mk]
    T = t + 1
    acc = m.GOLD if T == 7 else M                  # Onyxium: gold buckles + rims (v2 look)
    f = v2.Fig2()
    m.mannequin(f, back)
    sides = (0, 1)

    # ---------------- legs: gambeson trousers, cuisses, poleyns, greaves, boots + toe caps
    for side in sides:
        f.paint(S(rect(21, 48, 31, 74), side), GAMB, pattern=m.banded(56))
        f.paint(S(poly([(21, 52), (30, 52), (30, 57), (22, 57)]), side), M, kind='trim')   # lower cuisse lame
        f.paint(S(poly([(21, 48), (30, 48), (30, 53), (21, 53)]), side), M, kind='trim')   # upper cuisse
        f.paint(S(rect(21, 66, 31, 76), side), M, pattern=m.banded(73), kind='trim')  # greave
        if not back:
            f.paint(S(ell(20, 57, 31, 68), side), M, kind='trim')                      # poleyn (knee cop, front only)
            f.paint(S(poly([(21, 60), (18, 59), (18, 65), (21, 66)]), side), M, kind='trim')   # knee fan wing
        bm = S(rect(21, 75, 31, 82) | rect(19, 78, 31, 82), side)
        f.paint(bm, STRAP, pattern=m.banded(80))
        f.paint(S(rect(20, 75, 31, 77), side), STRAP, pattern=m.banded(76))          # boot strap
        m.buckle(f, X(24, side) - (3 if side else 0), 74, acc, w=4, h=4)
        if not back:
            f.trim(S(rect(19, 80, 31, 82), side), bm, acc)                            # steel toe cap
        else:
            f.trim(S(rect(21, 80, 31, 82), side), bm, STRAP)                          # heel
            f.paint(S(rect(22, 63, 30, 64), side), STRAP)                             # greave strap behind the knee

    # ---------------- arms: gambeson sleeve, rerebrace lames, couter, vambrace, gauntlet
    for side in sides:
        f.paint(S(rect(13, 30, 19, 46), side), GAMB, pattern=m.banded(38))
        f.paint(S(ell(11, 40, 21, 48), side), M, kind='trim')                        # couter
        f.paint(S(poly([(12, 47), (20, 47), (21, 53), (11, 53)]), side), M, pattern=m.banded(50), kind='trim')
        f.paint(S(poly([(10, 52), (22, 52), (21, 55), (11, 55)]), side), M, kind='trim')     # gauntlet cuff flare
        f.paint(S(rect(12, 55, 20, 60), side), M, pattern=m.banded(57), kind='trim')  # gauntlet + finger lames
        f.dots([(X(x, side), 60, 1) for x in (14, 16, 18)], M)

    # ---------------- torso: gambeson, sculpted breastplate + segmented belly lames (front) / backplate
    f.paint(rect(20, 20, 43, 49), GAMB, pattern=m.fine)
    if not back:
        lames = [poly([(22, 39), (41, 39), (41, 44), (22, 44)]),
                 poly([(21, 36), (42, 36), (42, 41), (21, 41)]),
                 poly([(21, 33), (42, 33), (42, 38), (21, 38)])]
        for lm in lames:                                                              # lowest first: upper overlaps
            f.paint(lm, M, kind='trim')
        chest = poly([(21, 19), (42, 19), (44, 25), (43, 31), (37, 35), (31.5, 36), (26, 35), (20, 31), (19, 25)])
        f.paint(chest, M, kind='trim')
    else:
        bp = poly([(20, 19), (43, 19), (44, 27), (43, 44), (20, 44), (19, 27)])
        f.paint(bp, M, pattern=m.banded(34, 39), kind='trim')

    # ---------------- sash wrapped under the belt + a SHORT knot tail (no skirt)
    f.paint(rect(19, 42, 44, 46), sash, pattern=v2.folds)
    if not back:
        f.paint(ell(24, 44, 29, 49), sash)                                            # knot
        f.paint(poly([(25, 48), (28, 48), (27, 56), (24, 55)]), sash, pattern=v2.folds)

    # ---------------- crossed leather straps (X) with a metal ring at the crossing
    s1 = poly([(19, 21), (22, 19), (44, 41), (41, 43)])
    s2 = mirror(s1)
    f.paint(s1, STRAP, pattern=m.banded())
    f.paint(s2, STRAP, pattern=m.banded())
    cx, cy = 31.5, 31
    ring = ell(28, 27, 35, 34)
    f.paint(ring, acc, kind='trim')
    f.paint(ell(30, 29, 33, 32), STRAP, outline=False)
    if not back:
        if T == 6:      # Mithril: glowing ore gem in the ring
            for (x, y) in ell(30, 29, 33, 32):
                v2.gpx(f, x, y, mix(M[3], hx(lp[0]), 0.5))
            v2.gpx(f, 31, 30, hx('#ffffff'))
        elif T == 7:    # Onyxium: violet crystal in a gold ring
            f.paint(ell(29, 28, 34, 33), v2.CRYSTAL, kind='trim')
            v2.gpx(f, 30, 29, hx('#ffffff'))
        else:
            f.paint(ell(30, 29, 33, 32), M, kind='trim')                               # metal boss

    # ---------------- buckled belts: wide belt + slung tool belt
    belt = rect(19, 46, 44, 49)
    f.paint(belt, STRAP, pattern=m.banded(47))
    f.paint(poly([(19, 50), (44, 48), (44, 50), (19, 52)]), STRAP)                    # slung tool belt
    if not back:
        m.buckle(f, 29, 45, acc, w=6, h=5)
        m.buckle(f, 32, 49, acc, w=4, h=3)
        # ore pouch (right hip) + little pick (left hip)
        f.paint(rect(37, 49, 44, 57), STRAP)
        f.paint(rect(37, 49, 44, 51), STRAP, pattern=lambda x, y, i: max(1, i - 1) if i else 0)
        f.dots([(40, 51, 3), (41, 51, 2)], acc)
        f.paint(line([(19, 50), (19, 61)], 1), STRAP)
        f.paint(poly([(15, 51), (19, 49), (23, 51), (19, 52)]), M, kind='trim')
    else:
        # lamp battery clipped on the belt + cable up to the helmet
        f.paint(rect(28, 43, 35, 51), STRAP)
        f.dots([(29, 44, 4), (30, 44, 3), (34, 50, 1)], STRAP)
        f.paint(rect(30, 45, 33, 46), acc, kind='trim')
        f.paint(line([(31, 43), (31, 34)], 1), m.LEATHER)
        f.paint(line([(31, 28), (31, 18)], 1), m.LEATHER)
        for x in (21, 42):
            f.dots([(x, 47, 3), (x, 48, 1)], acc)

    # ---------------- big rounded embossed pauldrons (lames first, dome on top)
    for side in sides:
        dome, l1, l2 = pauldron_masks(side)
        f.paint(l2, M, kind='trim')
        f.paint(l1, M, kind='trim')
        f.paint(dome, M, kind='trim')
        if T == 7:
            f.trim(bottom_rim(dome, 1) & dome, dome, m.GOLD)
            f.trim(bottom_rim(l2, 1) & l2, l2, m.GOLD)
        f.paint(S(ell(12, 19, 18, 25), side), M, kind='trim')                        # centre boss
        f.paint(S(rect(22, 20, 25, 23), side), STRAP)                                 # pauldron strap to the gorget
        if T == 7:
            for cx_, h in ((10, 5), (14, 7), (18, 5)):                                # Onyxium crystal studs (v2 echo)
                f.paint(S(poly([(cx_ - 1.5, 16), (cx_, 15 - h), (cx_ + 1.5, 16)]), side), v2.CRYSTAL, kind='trim')

    # ---------------- gorget (helmet sits on it)
    f.paint(rect(24, 16, 39, 22), M if T != 7 else m.GOLD, pattern=m.banded(19), kind='trim')

    # ---------------- the v2 helmet + lamp
    helmet(f, T, M, back, lp)
    return f


# ================================================================ FINE pass (paints on the 2x grid)
class Fine:
    def __init__(self, im, M):
        self.im, self.px, self.M = im, im.load(), M
        self.idx = {M[i]: i for i in range(1, 5)}

    def at(self, x, y):
        if 0 <= x < self.im.width and 0 <= y < self.im.height:
            return self.idx.get(self.px[x, y])
        return None

    def put(self, x, y, i):
        if self.at(x, y) is not None:
            self.px[x, y] = self.M[max(1, min(4, i))]

    def emboss(self, pts, raised=True):
        """1 fine px ridge: light on the line, shade 1 px down-right (engraved = reversed)"""
        P = set(pts)
        for x, y in P:
            if self.at(x, y) is None:
                continue
            self.put(x, y, 4 if raised else 1)
            q = (x + 1, y + 1)
            if q not in P:
                self.put(q[0], q[1], 1 if raised else 4)

    def rivet(self, x, y):
        if self.at(x, y) is None:
            return
        for dx, dy, i in ((0, 0, 4), (1, 0, 3), (0, 1, 3), (1, 1, 2), (2, 1, 1), (1, 2, 1), (2, 2, 1)):
            self.put(x + dx, y + dy, i)


def G(x, y):
    """64-grid coordinate -> fine coordinate"""
    return int(round(2 * x)), int(round(2 * (y + TOPR)))


def fm(pts, side):
    return [(127 - x if side else x, y) for x, y in pts]


def arc(cx, cy, rx, ry, a0, a1, n=None):
    n = n or int(abs(a1 - a0) * max(rx, ry) * 1.6) + 2
    out = []
    for k in range(n + 1):
        a = a0 + (a1 - a0) * k / n
        p = (int(round(cx + rx * math.cos(a))), int(round(cy + ry * math.sin(a))))
        if not out or out[-1] != p:
            out.append(p)
    return out


def spiral(cx, cy, r0, r1, a0, turns, sx=1):
    out = []
    n = int(turns * 70)
    for k in range(n + 1):
        u = k / n
        a = a0 + sx * u * turns * 2 * math.pi
        r = r0 + (r1 - r0) * u
        p = (int(round(cx + r * math.cos(a))), int(round(cy + r * math.sin(a))))
        if not out or out[-1] != p:
            out.append(p)
    return out


def segs(*pairs):
    """straight fine lines"""
    out = []
    for (x0, y0), (x1, y1) in pairs:
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for k in range(n + 1):
            out.append((round(x0 + (x1 - x0) * k / n), round(y0 + (y1 - y0) * k / n)))
    return out


def fine_pass(im, t, back):
    name, band, mk, lp, sash, wear, staged = TIERS[t]
    M = m.METALS[mk]
    F = Fine(im, M)
    for side in (0, 1):
        # --- pauldron: raised rim, scroll pair, rivets round the boss, lame edge rivets
        pcx, pcy = G(14.5, 23)
        F.emboss(fm(arc(pcx, pcy + 1, 15, 12, math.pi * 1.02, math.pi * 1.98), side))     # rim, upper arc
        F.emboss(fm(arc(pcx, pcy + 1, 15, 12, -0.05, 0.5), side) + fm(arc(pcx, pcy + 1, 15, 12, math.pi - 0.5, math.pi + 0.05), side))
        F.emboss(fm(spiral(pcx - 8, pcy + 6, 1, 5, 0, 1.3, 1), side))                 # scroll (outer)
        F.emboss(fm(spiral(pcx + 8, pcy + 6, 1, 5, math.pi, 1.3, -1), side))           # scroll (inner)
        F.emboss(fm(arc(pcx, pcy - 1, 8, 6, math.pi * 1.1, math.pi * 1.9), side), raised=False)   # engraved arch over the boss
        for a in (0.6, 1.3, 2.0, 2.7):
            F.rivet(*fm([(int(pcx + 6 * math.cos(a + math.pi)), int(pcy + 1 + 5 * math.sin(a + math.pi)))], side)[0])
        for x, y in ((11, 31), (17.5, 31), (12, 35), (17, 35)):
            F.rivet(*fm([G(x, y)], side)[0])
        # --- arms: lame highlights, couter rosette, knuckle studs
        if not back:
            F.emboss(fm(arc(*G(16, 44), 5, 4, 0, 2 * math.pi), side))
            F.rivet(*fm([G(15.6, 43.6)], side)[0])
        for x in (13, 15.5, 18):
            F.rivet(*fm([G(x, 55.6)], side)[0])
        F.emboss(fm(segs((G(11, 52.5), G(21, 52.5))), side))
        # --- legs: cuisse lame lines + rivets, poleyn fan arcs, greave ridge
        F.emboss(fm(segs((G(21.5, 48.5), G(29.5, 48.5)), (G(22, 52.5), G(29.5, 52.5))), side))
        for x in (22.5, 28):
            F.rivet(*fm([G(x, 50)], side)[0])
            F.rivet(*fm([G(x, 54)], side)[0])
        if not back:
            F.emboss(fm(arc(*G(25.5, 62.5), 7, 7, math.pi * 1.15, math.pi * 1.85), side))
            F.emboss(fm(arc(*G(25.5, 62.5), 3, 3, 0, 2 * math.pi), side))
        F.emboss(fm(segs((G(26, 67), G(26, 72))), side))
        F.emboss(fm(segs((G(25.5, 67), G(25.5, 72))), side), raised=False)
        F.emboss(fm(segs((G(21.5, 66.5), G(30.5, 66.5))), side))
        if not back:
            F.emboss(fm(segs((G(18.5, 61), G(20.5, 61.5)), (G(18.5, 63.5), G(20.5, 63.5))), side), raised=False)
    if not back:
        # --- sculpted breastplate: centre ridge + pec curves, lame top edges, rivets at lame ends
        cx = 63
        F.emboss(segs(((cx, 2 * (19 + TOPR) + 3), (cx, 2 * (27 + TOPR)))))
        F.emboss(segs(((cx + 1, 2 * (19 + TOPR) + 3), (cx + 1, 2 * (27 + TOPR)))), raised=False)
        F.emboss(arc(cx - 11, 2 * (24 + TOPR), 11, 9, math.pi * 0.15, math.pi * 0.95))
        F.emboss(arc(cx + 12, 2 * (24 + TOPR), 11, 9, math.pi * 0.05, math.pi * 0.85))
        F.emboss(arc(cx, 2 * (19 + TOPR), 10, 5, 0.1, math.pi - 0.1), raised=False)   # neckline engraved
        for y in (33, 36, 39):
            F.emboss(segs((G(21.5, y + 0.5), G(42, y + 0.5))))
            F.rivet(*G(22, y + 1.5))
            F.rivet(*G(41, y + 1.5))
    else:
        F.emboss(segs(((63, 2 * (20 + TOPR)), (63, 2 * (33 + TOPR)))))                  # spine ridge
        F.emboss(segs(((64, 2 * (20 + TOPR)), (64, 2 * (33 + TOPR)))), raised=False)
        for y in (34, 39):
            F.emboss(segs((G(20.5, y + 0.5), G(43, y + 0.5))))
        F.emboss(arc(G(31.5, 19)[0], G(31.5, 19)[1], 14, 6, 0.1, math.pi - 0.1))
    # --- scratches + patina (deterministic)
    W2, H2 = im.size
    for k in range(70):
        h = v2.hsh(k, t, 11 + back)
        x, y = (h * 7 + k * 37) % W2, (v2.hsh(k, t, 5 + back) * 3 + k * 23) % H2
        if F.at(x, y) in (2, 3) and F.at(x + 2, y + 1) in (2, 3):
            F.put(x, y, 1)
            F.put(x + 1, y, 1)
            F.put(x + 2, y + 1, 4)
    if wear:
        wc = hx(wear)
        for k in range(260):
            x = v2.hsh(k, t, 21 + back) % W2
            y = v2.hsh(k, t, 37 + back) * H2 // 256
            i = F.at(x, y)
            if i is not None and i <= 2 and F.at(x, y + 1) is not None:
                F.px[x, y] = mix(M[i], wc, 0.55)
                if v2.hsh(k, t, 3) < 90 and F.at(x + 1, y) is not None:
                    F.px[x + 1, y] = mix(M[F.at(x + 1, y)], wc, 0.35)
    return im


# ================================================================ sheet
def figure(t, back):
    return v2.show(fine_pass(v2.up2(draw_miner3(t, back)), t, back))


def main():
    m.TOP = TOPR
    n = len(TIERS)
    fronts = [figure(i, False) for i in range(n)]
    backs = [figure(i, True) for i in range(n)]
    fw, fh = fronts[0].size
    gap, top, labh = 18, 104, 58
    sw, sh = n * fw + (n + 1) * gap, top + 2 * (fh + labh) + gap * 3
    sheet = Image.new('RGBA', (sw, sh), m.BG)
    d = ImageDraw.Draw(sheet)
    sub = (60, 64, 70, 255)
    d.text((sw // 2, 14), 'SkyWynn Mining Armor - v3 HALF PLATE (cloud draft)', font=m.font(38), fill=m.INK, anchor='mt')
    d.text((sw // 2, 60), 'every tier the same half-plate miner outfit in its own metal: embossed round pauldrons, sculpted '
           'segmented breastplate, plate arms + gauntlets, crossed straps + buckled belts, plated greaves - no skirt', font=m.font(18),
           fill=sub, anchor='mt')
    d.text((sw // 2, 82), 'v2 helmets kept (Skyy likes the heads); every lamp must REALLY light (SkyyAccessories Lantern code) '
           '| 128 x 192 per figure, shown x3', font=m.font(16), fill=sub, anchor='mt')
    for i, row in enumerate(TIERS):
        name, band, mk, lp, sash, wear, staged = row
        x = gap + i * (fw + gap)
        sheet.paste(fronts[i], (x, top))
        d.text((x + fw // 2, top + fh + 6), f'T{i + 1} {name}', font=m.font(24), fill=m.INK, anchor='mt')
        d.text((x + fw // 2, top + fh + 34), band + ('  - STAGED' if staged else '') + '  (front)', font=m.font(15),
               fill=sub, anchor='mt')
        M = m.METALS[mk]
        for j, col in enumerate([M[3], M[2], M[1], sash[2], hx(lp[0])]):
            d.rectangle((x + 8 + j * 18, top + 8, x + 22 + j * 18, top + 22), fill=col, outline=(30, 30, 34, 255))
        y2 = top + fh + labh + gap
        sheet.paste(backs[i], (x, y2))
        d.text((x + fw // 2, y2 + fh + 6), f'T{i + 1} {name} (back)', font=m.font(17), fill=sub, anchor='mt')
    v2.OUT = HERE
    v2.save(sheet, 'mining-sheet-v3.png')
    print('wrote mining-sheet-v3.png', sheet.size)


if __name__ == '__main__':
    main()
