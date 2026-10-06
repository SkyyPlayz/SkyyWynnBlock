#!/usr/bin/env python3
"""SkyWynn Foraging Armor - concept sheets (cloud draft 2026-10-06).

Original pixel art, drawn from code (no copied art, no game files).
Run:  python3 research/cloud/foraging-armor/make_sheets.py
Writes the PNGs next to this script. Deterministic: same code -> same bytes.

Same style as research/cloud/light-armor/make_sheets.py (helpers copied, not
imported): every figure is painted on a 64 x 84 pixel grid, one "part" at a
time; each part gets a 1-px dark outline and a 4-step ramp lit from the
top-left; the grid is scaled up with NEAREST.

The look (research/cloud/Foraging-Armor-Design.md section 7 + Skyy's bark
reference, described in words): layered bark-plate chest, jagged bark tassels
at the hem, twisting vine / root trims over shoulders and collar, a glowing
sap / leaf-vein pattern branching up the chest, small leaves, wrapped bark
gauntlets, a bark crown (hood on Goldenwood). Each tier echoes one metal
armor's shapes (Copper ... Onyxium) but stays obviously wood.
"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__))
W, H = 64, 84
TOP = 8                # extra rows above the grid for crowns / spikes / hood
SCALE = 5
CHEST_SCALE = 8


def hx(s):
    s = s.lstrip('#')
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def ramp(*cols):
    """[outline, dark, mid, light, highlight]"""
    return [hx(c) for c in cols]


# ---------------------------------------------------------------- palettes
DUMMY = ramp('#4a453f', '#7e776c', '#968e81', '#ada596', '#c6bfb0')    # neutral mannequin
GOLD = ramp('#4a3208', '#9a6e18', '#d4a234', '#f0c860', '#fff0b0')
PANTS = ramp('#121410', '#22261e', '#2e3328', '#3b4234', '#4c5444')   # dark moss-grey cloth
VINE = ramp('#14260e', '#2e5020', '#43702c', '#5e9038', '#86b450')
LEAF_GREEN = ramp('#163010', '#2e5a1c', '#447e26', '#62a432', '#94cc54')

# name, band, echo, wood ramp, trim ramp, leaf ramp, sap (core colour, strength 0..1)
TIERS = [
    ('Wood', 'Lv 1-13', 'vanilla', None, None, None, None),   # tier 0 = vanilla Wood armor: placeholder only
    ('Softwood', 'Lv 10-18', 'Copper',
     ramp('#3a2814', '#8a6a42', '#b08c5c', '#ccab78', '#e6cc9c'),
     ramp('#3a2a14', '#7a6034', '#a68650', '#c8a868', '#e2c88a'),        # rope lashings
     LEAF_GREEN, ('#b4d07a', 0.30)),
    ('Lightwood', 'Lv 15-23', 'Iron',
     ramp('#34312c', '#8e8a82', '#b6b2a8', '#d6d2c8', '#f0ede6'),
     ramp('#1e140c', '#4a3220', '#644630', '#80603e', '#9c7a50'),        # dark wooden pegs
     LEAF_GREEN, ('#9ee886', 0.50)),
    ('Hardwood', 'Lv 20-28', 'Thorium',
     ramp('#2a160a', '#5e3a1c', '#7e5028', '#9e6a38', '#c08a52'),
     ramp('#1c0e06', '#3e2410', '#563418', '#6e4622', '#8a5a2e'),        # root collar
     LEAF_GREEN, ('#66f060', 0.75)),
    ('Drywood', 'Lv 25-38', 'Cobalt',
     ramp('#30281f', '#7a6c5a', '#9a8c78', '#b8ab96', '#d6cbb6'),
     ramp('#2e2a16', '#6a6436', '#8a844a', '#aaa462', '#cac482'),        # dry vine
     ramp('#3a2c0e', '#7a6020', '#a08030', '#c4a448', '#e0c870'), ('#dcf27a', 0.80)),
    ('Darkwood', 'Lv 35-43', 'Adamantite',
     ramp('#0c0705', '#2a1a12', '#3a261a', '#4e3424', '#684832'),
     ramp('#07050a', '#241a22', '#3a2c34', '#544450', '#70606a'),        # thorns
     ramp('#0a2420', '#164a40', '#226656', '#34866e', '#5aa88c'), ('#46f2d4', 0.95)),
    ('Redwood', 'Lv 40-49', 'Mithril',
     ramp('#2a0a08', '#6a1e16', '#8e2c1e', '#b0402a', '#d2603e'),
     ramp('#2a1006', '#5a2a12', '#7a3c1c', '#9a5226', '#b86c34'),        # curling roots (+ gold knots)
     ramp('#1c3a0c', '#3a7018', '#52941e', '#74b82c', '#a2da50'), ('#86ff6c', 1.0)),
    ('Goldenwood', 'Lv 50-59', 'Onyxium',
     ramp('#2a1606', '#5c3414', '#7a4a1c', '#9a6428', '#bc843a') + [hx('#f0c860')],   # heartwood + gold streak (index 5)
     GOLD,                                                               # gold leaf inlays
     GOLD, ('#fff8cc', 1.0)),
]

BG = hx('#b4b9bf')
BG_SHADOW = hx('#9ca2a9')
INK = (34, 36, 40, 255)


# ---------------------------------------------------------------- mask helpers (copied from light-armor)
def rect(x0, y0, x1, y1):
    return {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}


def _draw(fn):
    im = Image.new('1', (W, H + TOP), 0)
    d = ImageDraw.Draw(im)
    fn(d)
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


def hsh(x, y, s=0):
    """small deterministic hash 0..255"""
    v = (x * 73856093) ^ (y * 19349663) ^ (s * 83492791)
    v = (v ^ (v >> 13)) * 1274126177
    return (v >> 7) & 0xff


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3)) + (255,)


# ---------------------------------------------------------------- painter
class Fig:
    def __init__(self):
        self.im = Image.new('RGBA', (W, H + TOP), (0, 0, 0, 0))
        self._px = self.im.load()
        self.kind = {}
        fig = self

        class _PX:      # grid coords (y may be -TOP .. H-1) -> image coords
            def __getitem__(self, p):
                return fig._px[p[0], p[1] + TOP]

            def __setitem__(self, p, v):
                fig._px[p[0], p[1] + TOP] = v
        self.px = _PX()

    def paint(self, mask, rp, pattern=None, outline=True, edge_ref=None, kind='wood'):
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
            self.px[x, y] = rp[i]
            self.kind[(x, y)] = kind

    def dots(self, pts, rp, kind='trim'):
        for x, y, i in pts:
            if 0 <= x < W and -TOP <= y < H:
                self.px[x, y] = rp[i]
                self.kind[(x, y)] = kind

    def trim(self, rim, parent, rp, kind='trim'):
        self.paint(rim, rp, edge_ref=parent, kind=kind)

    def glow(self, pts, core, strength, halo=True):
        """sap veins: core pixels tinted toward the glow colour; a soft halo on stronger tiers"""
        pts = {p for p in pts if p in self.kind}
        if halo and strength >= 0.7:
            ring = {(x + dx, y + dy) for x, y in pts for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))} - pts
            for p in ring:
                if p in self.kind and self.kind[p] == 'wood':
                    self.px[p] = mix(self.px[p], core, 0.30 * strength)
        for p in pts:
            self.px[p] = mix(self.px[p], core, strength)
            self.kind[p] = 'sap'


# ---------------------------------------------------------------- patterns
def bark(t, seed=0):
    """vertical bark grain: grooves every 3-4 px with breaks, ridges lit on the left"""
    def f(x, y, i):
        if i == 0:
            return 0
        off = hsh(x // 4, y // 5, seed) % 2
        g = (x + off) % 4
        h = hsh(x, y, seed + 7)
        if t == 4 and h < 18:               # Drywood: cracked, split bark
            return 0
        if t == 2 and (y + x // 4 * 3) % 7 == 0 and g in (1, 2):   # Lightwood: birch marks
            return 0
        if t == 7 and g == 2 and hsh(x // 4, y // 9, seed + 3) % 3 == 0 and i:   # Goldenwood: gold streaks
            return 5
        if g == 0:
            return 1 if h > 40 else i
        if g == 1 and i >= 2:
            return 3 if t != 6 else i      # Redwood: smoother, less grain
        if i == 2 and h < 22:
            return 1
        return i
    return f


def wrap_pat(x, y, i):
    """diagonal wrapping (bark gauntlets, rope, vines)"""
    if i == 0:
        return 0
    return 1 if (x + y) % 3 == 0 else (3 if (x + y) % 3 == 1 and i >= 2 else i)


def banded(*rows):
    def f(x, y, i):
        return 1 if i in (2, 3, 4) and y in rows else i
    return f


LEAF = ["...44",
        "..432",
        ".3321",
        ".221.",
        "0...."]


def leaf(fig, x, y, rp, flip=False, kind='leaf'):
    pts = []
    for dy, row in enumerate(LEAF):
        for dx, ch in enumerate(row):
            if ch != '.':
                pts.append(((x + 4 - dx) if flip else (x + dx), y + dy, int(ch)))
    fig.dots(pts, rp, kind=kind)


def X(x, side):
    return x if side == 0 else W - 1 - x


def S(m, side):
    return m if side == 0 else mirror(m)


def vine(fig, pts, rp, w=2):
    """a twisting vine: a 2-px line along pts with a light twist stripe"""
    m = line(pts, w)
    fig.paint(m, rp, pattern=wrap_pat, kind='trim')
    return m


# ---------------------------------------------------------------- tier config
def cfg_for(t):
    c = dict(rope=False, pegs=False, thick=False, root_collar=0, knot=None, vcut=False, peak=False,
             thorns=False, tall=0, curls=False, gold=False, hood=False, knee=None, tassel='jag',
             vines=2, leaves=1, elbow=False)
    if t == 1:   # Softwood / Copper: open plates, thin bands, rope lashings, one vine
        c.update(rope=True, vines=1, knot='lashing')
    if t == 2:   # Lightwood / Iron: layered plates + pegs, leaf tassels
        c.update(pegs=True, tassel='leaf', knot='plate', elbow=True)
    if t == 3:   # Hardwood / Thorium: thick shoulders, heavy root collar, round knot boss
        c.update(thick=True, root_collar=3, knot='boss', knee='cap', elbow=True)
    if t == 4:   # Drywood / Cobalt: angular cuirass, V cut, peaked shoulders, pointed tassels
        c.update(vcut=True, peak=True, knot='rhombus', knee='point', tassel='point', root_collar=2)
    if t == 5:   # Darkwood / Adamantite: tall thorn-spiked pauldrons
        c.update(thorns=True, knot='thornknot', knee='spike', tassel='point', root_collar=2, elbow=True)
    if t == 6:   # Redwood / Mithril: smooth, tall collar, curling roots, gold knots
        c.update(tall=2, curls=True, knot='gem', knee='cap', root_collar=3, leaves=2, elbow=True)
    if t == 7:   # Goldenwood / Onyxium: ornate, hooded, full, gold leaf inlays
        c.update(tall=2, curls=True, gold=True, hood=True, knot='heart', knee='cap', root_collar=3,
                 leaves=3, elbow=True)
    return c


# ---------------------------------------------------------------- sap-vein shapes (front chest, back spine)
VEIN_FRONT = [
    [(31, 46), (31, 40), (32, 35), (31, 30), (31, 25)],         # trunk
    [(31, 40), (28, 37), (26, 33), (24, 30)],
    [(32, 38), (35, 35), (37, 31), (39, 28)],
    [(31, 33), (28, 30), (27, 26)],
    [(32, 31), (35, 28), (36, 25)],
    [(26, 33), (23, 34)],
    [(37, 31), (40, 33)],
]
VEIN_BACK = [
    [(31, 46), (31, 38), (32, 30), (31, 24)],
    [(31, 40), (27, 36), (25, 31)],
    [(32, 35), (36, 32), (38, 28)],
]


def vein_pts(paths):
    pts = set()
    for p in paths:
        pts |= line(p, 1)
    return pts


# ---------------------------------------------------------------- the figure
def draw_figure(t, back=False, bust=False):
    name, band, echo, WD, TR, LF, sap = TIERS[t]
    c = cfg_for(t)
    core, strength = hx(sap[0]), sap[1]
    f = Fig()
    sides = (0, 1)
    WD_IN = [mix(col, (10, 8, 6), 0.45) for col in WD]       # far side / inner bark (darker)

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

    # --- side tassels behind the legs (far, darker)
    if not bust:
        for side in sides:
            for x0, y1 in ((15, 59), (17, 62)):
                m = S(poly([(x0, 47), (x0 + 4, 47), (x0 + 4, y1 - 2), (x0 + 2, y1 + 1), (x0, y1 - 3)]), side)
                f.paint(m, WD_IN)

    # --- legs: moss cloth trousers, bark greaves, bark boots with wrapped tops
    if not bust:
        for side in sides:
            f.paint(S(rect(21, 48, 31, 72), side), PANTS, kind='cloth')
            gm = S(poly([(21, 60), (31, 60), (31, 73), (21, 73)]), side)
            f.paint(gm, WD, pattern=bark(t, 3 + side))
            km = S(ell(21, 57, 31, 65), side)
            if c['knee'] == 'cap' or c['knee'] is None:
                f.paint(km, WD, pattern=bark(t, 5 + side) if c['knee'] is None else None)
                if c['knee'] == 'cap':
                    f.trim(top_rim(km, 2), km, TR)
            if c['knee'] in ('point', 'spike') and not back:
                f.paint(km, WD, pattern=bark(t, 5 + side))
                if c['knee'] == 'point':
                    f.paint(S(poly([(22, 62), (26, 55), (30, 62)]), side), TR)
                else:
                    f.paint(S(poly([(24, 60), (26, 52), (28, 60)]), side), TR)
            elif c['knee'] in ('point', 'spike'):
                f.paint(km, WD, pattern=bark(t, 5 + side))
            bm = S(rect(21, 74, 31, 82) | rect(20, 77, 31, 82), side)
            f.paint(bm, WD_IN if back else WD, pattern=banded(80))
            f.paint(S(rect(20, 72, 31, 75), side), TR if (c['rope'] or t >= 3) else VINE, pattern=wrap_pat)

    # --- jagged bark tassel skirt
    if not bust:
        xs = [19, 23, 27, 31, 35, 39] if not back else [17, 21, 25, 29, 33, 37, 41]
        for k, x0 in enumerate(xs):
            y1 = 62 + (hsh(k, t, 11) % 4) - (2 if k % 2 else 0)
            if back:
                y1 = 62 + (hsh(k, t, 13) % 4)
            if c['tassel'] == 'point':
                tm = poly([(x0, 47), (x0 + 4, 47), (x0 + 4, y1 - 2), (x0 + 2, y1 + 3), (x0, y1 - 2)])
            elif c['tassel'] == 'leaf':
                tm = poly([(x0, 47), (x0 + 4, 47), (x0 + 4, y1 - 3), (x0 + 2, y1 + 2), (x0, y1 - 3)])
            else:   # jagged: uneven sawtooth end
                j = hsh(k, t, 17) % 3
                tm = poly([(x0, 47), (x0 + 4, 47), (x0 + 4, y1 - j), (x0 + 3, y1 + 1),
                           (x0 + 2, y1 - 2), (x0 + 1, y1 + 2 - j), (x0, y1 - 1)])
            f.paint(tm, WD, pattern=bark(t, 20 + k))
            if c['tassel'] == 'leaf':
                tipl = clip(tm, y0=y1 - 3)
                f.trim(tipl, tm, LF, kind='leaf')
            if c['pegs']:
                f.dots([(x0 + 2, 50, 4), (x0 + 2, 51, 1)], TR)
            if c['gold'] and k % 2 == 0:
                f.dots([(x0 + 2, y1 - 4, 4), (x0 + 2, y1 - 3, 2)], GOLD)

    # --- arms: bark upper arm, elbow knot, wrapped bark gauntlet, finger-less wraps
    for side in sides:
        f.paint(S(rect(13, 33, 19, 40), side), WD, pattern=bark(t, 30 + side))
        em = S(ell(12, 39, 20, 46), side)
        f.paint(em, WD)
        if c['elbow']:
            f.trim(top_rim(em, 2), em, TR)
        if c['thorns']:
            f.paint(S(poly([(12, 41), (7, 43), (12, 45)]), side), TR)
        if c['vcut'] and not back:
            f.paint(S(poly([(12, 41), (8, 44), (12, 45)]), side), TR)
        br = S(poly([(13, 46), (19, 46), (20, 54), (12, 54)]), side)
        f.paint(br, WD, pattern=bark(t, 40 + side))
        wrap = S(rect(12, 49, 20, 50) | rect(12, 52, 20, 52), side)
        f.paint(wrap & br, TR if t != 4 else VINE, pattern=wrap_pat, kind='trim')
        if c['pegs']:
            f.dots([(X(14, side), 47, 4), (X(18, side), 47, 4)], TR)
        f.paint(S(rect(13, 54, 19, 56), side), TR if t != 7 else WD, pattern=wrap_pat)
        f.paint(S(rect(13, 56, 19, 58), side), DUMMY, kind='dummy')
        f.dots([(X(x, side), 57, 1) for x in (15, 17)], DUMMY, kind='dummy')

    # --- chest: layered bark plates (lowest first, each upper plate overlaps with a jagged edge)
    torso = rect(20, 21, 43, 48) | rect(21, 20, 42, 21)
    f.paint(torso, WD_IN)
    if c['vcut'] and not back:
        rows = [(36, 48, 'v'), (28, 40, 'v'), (20, 32, 'v')]
    else:
        rows = [(38, 48, 'j'), (30, 40, 'j'), (20, 32, 'j')]
    for k, (y0, y1, kind) in enumerate(rows):
        if kind == 'v':
            pm = poly([(20, y0), (43, y0), (43, y1 - 4), (32, y1), (31, y1), (20, y1 - 4)])
        else:
            pts = [(20, y0), (43, y0), (43, y1)]
            for x in range(43, 19, -3):      # jagged lower edge
                pts.append((x - 1, y1 - 1 - hsh(x, k, t) % 3))
            pts.append((20, y1))
            pm = poly(pts)
        pm = (pm & torso) | clip(pm, y0=y0, y1=y1, x0=20, x1=43)
        f.paint(pm, WD, pattern=bark(t, 50 + k))
        if c['pegs']:
            for px_ in (22, 41):
                f.dots([(px_, y0 + 2, 4), (px_, y0 + 3, 1)], TR)
        if c['rope'] and k < 2 and not back:
            r = clip(rect(20, y0 + 1, 43, y0 + 2), x0=20, x1=43)
            f.paint(r, TR, pattern=wrap_pat, edge_ref=torso)
    if not back:
        # Softwood: "open plates" - a gap down the middle shows the cloth under-shirt
        if t == 1:
            f.paint(rect(30, 24, 33, 46), PANTS, kind='cloth')
            for y in (27, 31, 35, 39, 43):    # rope lacing across the gap
                f.dots([(29, y, 3), (30, y, 3), (31, y + 1, 3), (32, y + 1, 3), (33, y, 3), (34, y, 3)], TR)
        # sap veins up the chest
        f.glow(vein_pts(VEIN_FRONT), core, strength)
        if c['gold']:
            for x, y in ((24, 28), (38, 28), (25, 42), (37, 42)):
                leaf(f, x - 2, y - 2, GOLD, flip=x > 31, kind='trim')
    else:
        if t >= 3:
            f.glow(vein_pts(VEIN_BACK), core, strength * 0.8)

    # --- vine belt (twisted) with a tier knot / clasp
    b1 = rect(19, 42, 44, 46)
    f.paint(b1, VINE if t not in (4, 7) else TR, pattern=wrap_pat)
    if not back:
        for side in sides:
            leaf(f, X(21, side) - (4 if side else 0), 38, LF, flip=bool(side))
        kn = c['knot']
        if kn == 'lashing':
            f.paint(rect(29, 41, 34, 47), TR, pattern=wrap_pat)
        elif kn == 'plate':
            f.paint(rect(28, 40, 35, 47), WD)
            f.dots([(29, 41, 4), (34, 41, 4), (29, 46, 1), (34, 46, 1)], TR)
        elif kn == 'boss':
            f.paint(ell(26, 38, 37, 49), TR)
            f.paint(ell(29, 41, 34, 46), WD)
            f.dots([(30, 42, 4), (31, 42, 3), (30, 43, 3)], WD)
        elif kn == 'rhombus':
            f.paint(poly([(31.5, 38), (37, 44), (31.5, 50), (26, 44)]), TR)
            f.paint(poly([(31.5, 41), (34, 44), (31.5, 47), (29, 44)]), WD)
        elif kn == 'thornknot':
            f.paint(ell(28, 40, 35, 47), TR)
            for a, b in (((27, 43), (23, 41)), ((36, 43), (40, 41)), ((31, 40), (31, 36))):
                f.paint(poly([a, b, (a[0] + (1 if a[0] < 31 else -1), a[1] + 2)]) | line([a, b], 1), TR)
        elif kn == 'gem':
            f.paint(ell(27, 39, 36, 48), TR)
            f.paint(ell(29, 41, 34, 46), GOLD)
            f.px[31, 43] = mix(GOLD[4], core, 0.6)
        elif kn == 'heart':
            f.paint(poly([(31.5, 36), (37, 43), (31.5, 51), (26, 43)]), GOLD)
            f.paint(ell(28, 40, 35, 47), GOLD)
            f.paint(ell(29, 41, 34, 46), WD)
            for p in ((31, 43), (32, 43), (31, 44), (32, 44)):
                f.px[p] = hx('#fffbe6')
            f.px[30, 42] = core

    # --- root / vine collar
    tall = c['tall']
    f.paint(rect(24, 18 - tall, 39, 24), WD_IN)
    for side in sides:
        flap = poly([(20, 16 - tall), (30, 18 - tall), (30, 25), (20, 25)]) if not back else \
            poly([(20, 16 - tall), (31, 18 - tall), (31, 25), (20, 25)])
        fm = S(flap, side)
        f.paint(fm, WD, pattern=bark(t, 60 + side))
        if c['root_collar']:
            f.trim(top_rim(fm, c['root_collar']), fm, TR if not c['gold'] else GOLD)
        if c['vcut']:
            f.paint(S(poly([(19, 19), (20, 12), (23, 17)]), side), WD)
        if c['thorns']:
            f.paint(S(poly([(20, 18), (21, 11), (23, 17)]), side), TR)
            f.paint(S(poly([(24, 18), (25, 13), (27, 18)]), side), TR)
    # vine twisting along the collar
    if c['vines'] >= 2 or t == 1:
        vine(f, [(21, 21), (25, 23), (29, 22), (31, 24), (34, 22), (38, 23), (42, 21)], VINE)
    if not back and c['leaves'] >= 2:
        for side in sides:
            leaf(f, X(26, side) - (4 if side else 0), 13 - tall, LF, flip=bool(side))

    # --- layered bark pauldrons (lowest plate first), vine wrapped over the top
    big = 1 if c['thick'] else 0
    p3 = clip(ell(12, 24, 20, 36), y0=30)
    p2 = clip(ell(11, 19, 22, 33), y0=26)
    p1 = ell(10 - big, 18 - big, 23 + big, 29 + big)
    for side in sides:
        for k, pm in ((3, p3), (2, p2), (1, p1)):
            pm = S(pm, side)
            f.paint(pm, WD, pattern=bark(t, 70 + k + side * 3))
            if k == 1 and (c['thick'] or c['curls']):
                f.trim(bottom_rim(pm, 2), pm, TR if not c['gold'] else GOLD)
            if k == 2 and c['pegs']:
                f.dots([(X(x, side), 30, 4) for x in (13, 16, 19)], TR)
        top = S(p1, side)
        if c['peak']:
            f.paint(S(poly([(12, 21), (15, 10), (19, 19)]), side), WD, pattern=bark(t, 90))
            f.trim(S(clip(poly([(12, 21), (15, 10), (19, 19)]), y1=14), side), S(poly([(12, 21), (15, 10), (19, 19)]), side), TR)
        if c['thorns']:
            for sx, h in ((11, 6), (14, 11), (17, 13), (21, 7)):
                f.paint(S(poly([(sx - 1.5, 21), (sx, 20 - h), (sx + 1.5, 21)]), side), TR)
        if c['gold']:   # crown points of gold leaf
            for sx, h in ((12, 4), (16, 6), (20, 4)):
                leaf(f, X(sx, side) - 2, 19 - h, GOLD, flip=bool(side), kind='trim')
        # the vine: over the top of the shoulder cap
        if c['vines'] >= 2 or side == 0:
            vp = [(X(9 - big, side), 27), (X(12, side), 21), (X(16, side), 24), (X(20, side), 19), (X(24, side), 22)]
            vine(f, vp, VINE if t != 4 else TR)
        if c['curls'] and not back:
            curl = [(10, 31), (9, 33), (10, 35), (12, 35), (13, 33)]
            f.paint(S(line(curl, 1), side), TR if not c['gold'] else GOLD, outline=False, kind='trim')
            f.dots([(X(16, side), 24, 4), (X(17, side), 24, 2)], GOLD)      # gold knot
        if not back and c['leaves'] >= 1:
            leaf(f, X(19, side) - (4 if side else 0), 16 - big, LF, flip=bool(side))
        if c['leaves'] >= 3 and not back:
            leaf(f, X(9, side) - (4 if side else 0), 24, LF, flip=bool(side))
        # shoulder sap line on bright tiers
        if strength >= 0.9 and not back:
            f.glow({(X(x, side), 25) for x in range(13, 19)}, core, strength * 0.7, halo=False)

    # --- head: bark crown, or the Goldenwood hood
    if not bust:
        if c['hood']:
            hood = poly([(31.5, -7), (38, -3), (42, 2), (43, 8), (43, 19), (20, 19), (20, 8), (21, 2), (25, -3)])
            f.paint(hood, WD, pattern=bark(t, 99))
            f.trim(bottom_rim(hood, 2), hood, GOLD)
            if not back:
                face = ell(24, 4, 39, 22) & rect(24, 4, 39, 17)
                f.paint(face, [mix(col, (6, 4, 2), 0.6) for col in WD])     # shadow inside the hood
                f.paint(clip(ell(26, 7, 37, 24), y1=17), DUMMY, kind='dummy')
                f.trim(clip(ell(23, 3, 40, 23) - face, y1=17) & hood, hood, GOLD)
                f.paint(poly([(31.5, -4), (34, -1), (31.5, 2), (29, -1)]), GOLD)
                f.px[31, -1] = core
                f.px[32, -1] = hx('#fffbe6')
            else:
                f.glow(line([(31, -4), (31, 17)], 1), core, strength * 0.8)
            for side in sides:
                leaf(f, X(20, side) - (4 if side else 0), -2, GOLD, flip=bool(side), kind='trim')
                leaf(f, X(25, side) - (4 if side else 0), -6, LF, flip=bool(side), kind='trim')
        else:
            cm = rect(22, 4, 41, 7)
            f.paint(cm, WD, pattern=bark(t, 98))
            f.trim(bottom_rim(cm, 1), cm, TR)
            pts_x = (24, 28, 31, 35, 39) if t != 1 else (25, 31, 38)
            for k, sx in enumerate(pts_x):
                h = (3 + (2 if k == len(pts_x) // 2 else 0)) * (2 if c['thorns'] else 1)
                if c['vcut']:
                    h += 1
                spike = poly([(sx - 1.5, 4), (sx, 4 - h), (sx + 1.5, 4)])
                f.paint(spike, TR if c['thorns'] else WD)
            if not back:
                leaf(f, 34, -1 if c['leaves'] >= 2 else 0, LF)
                if c['leaves'] >= 2:
                    leaf(f, 25, 0, LF, flip=True)
                f.glow({(x, 5) for x in range(28, 36)}, core, strength * 0.8, halo=False)
            vine(f, [(22, 7), (27, 5), (32, 7), (36, 5), (41, 7)], VINE if t != 4 else TR, w=1)
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


def label(im, text, sub, n=22):
    pad = 46
    out = Image.new('RGBA', (im.width, im.height + pad), BG)
    out.paste(im, (0, 0))
    d = ImageDraw.Draw(out)
    d.text((im.width // 2, im.height + 4), text, font=font(n), fill=INK, anchor='mt')
    d.text((im.width // 2, im.height + 27), sub, font=font(14), fill=(60, 64, 70, 255), anchor='mt')
    return out


def save(im, name):
    im = im.convert('RGB').quantize(colors=160, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(os.path.join(OUT, name), optimize=True)


def main():
    fronts, backs = [None], [None]
    for t, (name, band, echo, WD, TR, LF, sap) in enumerate(TIERS):
        if t == 0:
            continue   # tier 0 = vanilla Wood armor, no new design (Skyy 2026-10-05)
        fr, bk = draw_figure(t), draw_figure(t, back=True)
        a, b = scaled(fr, SCALE), scaled(bk, SCALE)
        pair = Image.new('RGBA', (a.width * 2 + 12, a.height), BG)
        pair.paste(a, (0, 0))
        pair.paste(b, (a.width + 12, 0))
        d = ImageDraw.Draw(pair)
        d.text((8, 6), 'front', font=font(14), fill=INK)
        d.text((a.width + 20, 6), 'back', font=font(14), fill=INK)
        save(label(pair, f'{name} Foraging Armor', f'{band}  |  echoes {echo}  |  concept, cloud draft'),
             f'{name.lower()}-set.png')
        fronts.append(a)
        backs.append(b)

    fw, fh = fronts[1].size
    gap, top, labh = 16, 70, 50
    n = len(TIERS)
    sheet_w = n * fw + (n + 1) * gap
    sheet_h = top + 2 * (fh + labh) + gap * 3
    sheet = Image.new('RGBA', (sheet_w, sheet_h), BG)
    d = ImageDraw.Draw(sheet)
    d.text((sheet_w // 2, 18), 'SkyWynn Foraging Armor - concept (cloud draft)', font=font(34), fill=INK, anchor='mt')
    for i, (name, band, echo, WD, TR, LF, sap) in enumerate(TIERS):
        x = gap + i * (fw + gap)
        y = top
        if fronts[i] is None:
            y2 = top + fh + labh + gap
            d.rectangle((x, y, x + fw - 1, y2 + fh - 1), fill=(166, 171, 177, 255), outline=(140, 145, 151, 255), width=3)
            for k, ln in enumerate(['Tier 0', 'vanilla Wood', 'armor', '(Armor_Wood)', '', '(no new design)']):
                d.text((x + fw // 2, y + 140 + k * 30), ln, font=font(22 if k < 4 else 18),
                       fill=(110, 114, 120, 255), anchor='mt')
            d.text((x + fw // 2, y + fh + 6), 'Wood', font=font(24), fill=(110, 114, 120, 255), anchor='mt')
            d.text((x + fw // 2, y + fh + 32), band + '  (vanilla)', font=font(14), fill=(110, 114, 120, 255), anchor='mt')
            continue
        sheet.paste(fronts[i], (x, y))
        d.text((x + fw // 2, y + fh + 6), name, font=font(24), fill=INK, anchor='mt')
        d.text((x + fw // 2, y + fh + 32), f'{band}  echoes {echo}', font=font(14), fill=(60, 64, 70, 255), anchor='mt')
        for j, col in enumerate([WD[3], WD[2], WD[1], TR[2], hx(sap[0])]):
            d.rectangle((x + 6 + j * 16, y + 6, x + 18 + j * 16, y + 18), fill=col, outline=WD[0])
        y2 = top + fh + labh + gap
        sheet.paste(backs[i], (x, y2))
        d.text((x + fw // 2, y2 + fh + 6), name + ' (back)', font=font(16), fill=(60, 64, 70, 255), anchor='mt')
    save(sheet, 'foraging-armor-sheet.png')
    print('wrote', len(os.listdir(OUT)), 'files in', OUT)


if __name__ == '__main__':
    main()
